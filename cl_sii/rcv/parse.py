import csv
from datetime import date
import logging
from typing import Mapping, Sequence, Tuple

import marshmallow
import marshmallow.fields
import marshmallow.validate

from cl_sii.dte.data_models import DteDataL2, TipoDteEnum
from cl_sii.extras import mm_fields
from cl_sii.libs import csv_utils
from cl_sii.libs import file_processing
from cl_sii.libs import mm_utils
from cl_sii.libs import tz_utils
from cl_sii.rut import Rut


logger = logging.getLogger(__name__)


class _RcvCsvDialect(csv.Dialect):

    """
    CSV dialect of RCV CSV files.

    The properties of this dialect were determined with the help of
    :class:`csv.Sniffer`.

    >>> import gzip
    >>> filename = 'SII-download-RCV-file-http-body-response.csv.gz'
    >>> with gzip.open(filename, 'rt', encoding='utf-8') as f:
    ...     dialect = csv.Sniffer().sniff(f.read(50 * 1024))

    """

    delimiter = ';'
    quotechar = '"'
    escapechar = None
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL


class RcvCsvRowSchema(marshmallow.Schema):

    FIELD_FECHA_RECEPCION_DT_TZ = tz_utils.TZ_CL_SANTIAGO
    FIELD_FECHA_ACUSE_DT_TZ = tz_utils.TZ_CL_SANTIAGO

    class Meta:
        strict = True

    emisor_rut = mm_fields.RutField(
        required=True,
        load_from='RUT Proveedor',
    )
    tipo_dte = marshmallow.fields.Integer(
        required=True,
        load_from='Tipo Doc',
    )
    folio = marshmallow.fields.Integer(
        required=True,
        load_from='Folio',
    )
    emisor_razon_social = marshmallow.fields.String(
        required=True,
        load_from='Razon Social',
    )
    fecha_emision_date = mm_utils.CustomMarshmallowDateField(
        format='%d/%m/%Y',  # e.g. '22/10/2018'
        required=True,
        load_from='Fecha Docto',
    )
    fecha_recepcion_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        load_from='Fecha Recepcion',
    )
    fecha_acuse_dt = marshmallow.fields.DateTime(
        format='%d/%m/%Y %H:%M:%S',  # e.g. '23/10/2018 01:54:13'
        required=True,
        allow_none=True,
        load_from='Fecha Acuse',
    )
    monto_total = marshmallow.fields.Integer(
        required=True,
        load_from='Monto Total',
    )

    ###########################################################################
    # fields whose value is set using data passed in the schema context
    ###########################################################################

    receptor_rut = mm_fields.RutField(
        required=True,
    )
    receptor_razon_social = marshmallow.fields.String(
        required=True,
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict) -> dict:
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Set field value only if it was not in the input data.
        in_data.setdefault('receptor_rut', self.context['receptor_rut'])
        in_data.setdefault('receptor_razon_social', self.context['receptor_razon_social'])

        # Fix missing/default values.
        if 'Fecha Acuse' in in_data:
            if in_data['Fecha Acuse'] == '':
                in_data['Fecha Acuse'] = None

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict) -> dict:
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13'
        data['fecha_recepcion_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
            dt=data['fecha_recepcion_dt'], tz=self.FIELD_FECHA_RECEPCION_DT_TZ)
        # >>> data['fecha_recepcion_dt'].isoformat()
        # '2018-10-23T01:54:13-03:00'
        # >>> data['fecha_recepcion_dt'].astimezone(pytz.UTC).isoformat()
        # '2018-10-23T04:54:13+00:00'

        # note: to express this value in another timezone (but the value does not change), do
        #   `dt_obj.astimezone(pytz.timezone('some timezone'))`

        if data['fecha_acuse_dt']:
            data['fecha_acuse_dt'] = tz_utils.convert_naive_dt_to_tz_aware(
                dt=data['fecha_acuse_dt'], tz=self.FIELD_FECHA_ACUSE_DT_TZ)

        return data

    @marshmallow.validates_schema(pass_original=True)
    def validate_schema(self, data: dict, original_data: dict) -> None:
        mm_utils.validate_no_unexpected_input_fields(self, data, original_data)

    # @marshmallow.validates('field_x')
    # def validate_field_x(self, value):
    #     pass

    def to_dte_data_l2(self, data: dict) -> DteDataL2:
        # note: the data of some serializer fields is not included in the returned struct.
        #   - fecha_recepcion_dt
        #   - fecha_acuse_dt

        try:
            emisor_rut: Rut = data['emisor_rut']  # type: ignore
            receptor_rut: Rut = data['receptor_rut']  # type: ignore
            tipo_dte_int = data['tipo_dte']  # type: ignore
            folio: int = data['folio']  # type: ignore
            fecha_emision_date: date = data['fecha_emision_date']  # type: ignore
            monto_total: int = data['monto_total']  # type: ignore
            emisor_razon_social: str = data['emisor_razon_social']  # type: ignore
            receptor_razon_social: str = data['receptor_razon_social']  # type: ignore
        except KeyError as exc:
            raise ValueError("Programming error: a referenced field is missing.") from exc

        try:
            tipo_dte = TipoDteEnum(tipo_dte_int)
            dte_data = DteDataL2(
                emisor_rut=emisor_rut,
                tipo_dte=tipo_dte,
                folio=folio,
                fecha_emision_date=fecha_emision_date,
                receptor_rut=receptor_rut,
                monto_total=monto_total,
                emisor_razon_social=emisor_razon_social,
                receptor_razon_social=receptor_razon_social,
                # fecha_vencimiento_date='',
                # firma_documento_dt_naive='',
                # signature_value='',
                # signature_x509_cert_pem='',
                # emisor_giro='',
                # emisor_email='',
                # receptor_email='',
            )
        except (TypeError, ValueError):
            raise

        return dte_data


# # FIXME
# def row_op(dte_data: DteDataL2) -> bool:
#     # logger.debug("DTE data %s", str(dte_data.as_dict()))
#     print(dte_data)
#     return True


# FIXME
def row_op(schema: RcvCsvRowSchema, deserialized_data: Mapping[str, object]) -> bool:
    # logger.debug("DTE data %s", str(dte_data.as_dict()))
    dte_data = schema.to_dte_data_l2(deserialized_data)
    print(dte_data)
    return True


def process_rcv_csv_file(
    rcv_owner_rut: Rut,
    rcv_owner_razon_social: str,
    input_file_path: str,
    output_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = None,
) -> Tuple[int, Sequence[Tuple[int, Mapping, Mapping]]]:
    """
    FIXME

    Process a RCV CSV file.

    """
    _CSV_ROW_DICT_EXTRA_FIELDS_KEY = '_extra_csv_fields_data'

    expected_input_field_names = (
        'Nro',
        'Tipo Doc',  # 'tipo_dte'
        'Tipo Compra',
        'RUT Proveedor',  # 'emisor_rut'
        'Razon Social',  # 'emisor_razon_social'
        'Folio',  # 'folio'
        'Fecha Docto',  # 'fecha_emision_date'
        'Fecha Recepcion',  # 'fecha_recepcion_dt'
        'Fecha Acuse',  # 'fecha_acuse_dt'
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Total',  # 'monto_total'
        'Monto Neto Activo Fijo',
        'IVA Activo Fijo',
        'IVA uso Comun',
        'Impto. Sin Derecho a Credito',
        'IVA No Retenido',
        'Tabacos Puros',
        'Tabacos Cigarrillos',
        'Tabacos Elaborados',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Impuesto',
        'Valor Otro Impuesto',
        'Tasa Otro Impuesto',
    )

    fields_to_remove_names = (
        'Nro',
        'Tipo Compra',
        'Monto Exento',
        'Monto Neto',
        'Monto IVA Recuperable',
        'Monto Iva No Recuperable',
        'Codigo IVA No Rec.',
        'Monto Neto Activo Fijo',
        'IVA Activo Fijo',
        'IVA uso Comun',
        'Impto. Sin Derecho a Credito',
        'IVA No Retenido',
        'Tabacos Puros',
        'Tabacos Cigarrillos',
        'Tabacos Elaborados',
        'NCE o NDE sobre Fact. de Compra',
        'Codigo Otro Impuesto',
        'Valor Otro Impuesto',
        'Tasa Otro Impuesto',
    )

    for _field_to_discard in fields_to_remove_names:
        assert _field_to_discard in expected_input_field_names

    fields_to_remove_names += (_CSV_ROW_DICT_EXTRA_FIELDS_KEY, )

    # TODO: use serializer for output.

    # Marshmallow schema fields whose value is set using data passed in the schema context.
    output_fields = expected_input_field_names + (
        'receptor_rut',
        'receptor_razon_social',
    )

    output_fields += (
        'row_op_return_values',
        'validation_errors',
        'row_op_errors',
    )

    row_errors = []
    n_rows_proccesed = 0

    input_csv_row_schema = RcvCsvRowSchema(context=dict(
        receptor_rut=rcv_owner_rut,
        receptor_razon_social=rcv_owner_razon_social,
    ))

    input_data_enc = 'utf-8'
    output_data_enc = 'utf-8'
    # note:
    #   > If csvfile is a file object, it should be opened with newline=''
    #   https://docs.python.org/3/library/csv.html#csv.reader
    with open(input_file_path, mode='rt', encoding=input_data_enc, newline='') as input_f:
        # Create a CSV reader, with auto-detection of header names (first row).
        csv_reader = csv_utils.create_csv_dict_reader(
            input_f,
            csv_dialect=_RcvCsvDialect,
            row_dict_extra_fields_key=_CSV_ROW_DICT_EXTRA_FIELDS_KEY,
            expected_fields_strict=True,
            expected_field_names=expected_input_field_names,
        )

        with open(output_file_path, mode='wt', encoding=output_data_enc, newline='') as output_f:
            csv_writer = csv.DictWriter(
                output_f,
                fieldnames=output_fields,
                dialect='unix',  # csv.unix_dialect
            )
            csv_writer.writeheader()

            g = file_processing.csv_rows_mm_deserialization_iterator(
                csv_reader,
                row_schema=input_csv_row_schema,
                n_rows_offset=n_rows_offset,
                max_n_rows=max_n_rows,
                fields_to_remove_names=fields_to_remove_names,
            )

            row_ix = 0
            for row_ix, row_data, deserialized_row_data, validation_errors in g:
                logger.debug("Processing row %s. Content: %s", row_ix, repr(row_data))

                if validation_errors:
                    row_op_return_values = ()
                    row_op_errors = None
                else:
                    # try:
                    #     emisor_rut: Rut = \
                    #         deserialized_row_data['emisor_rut']  # type: ignore
                    #     receptor_rut: Rut = \
                    #         deserialized_row_data['receptor_rut']  # type: ignore
                    #     tipo_dte_int = \
                    #         deserialized_row_data['tipo_dte']  # type: ignore
                    #     folio: int = \
                    #         deserialized_row_data['folio']  # type: ignore
                    #     fecha_emision_date: date = \
                    #         deserialized_row_data['fecha_emision_date']  # type: ignore
                    #     monto_total: int = \
                    #         deserialized_row_data['monto_total']  # type: ignore
                    #     emisor_razon_social: str = \
                    #         deserialized_row_data['emisor_razon_social']  # type: ignore
                    #     receptor_razon_social: str = \
                    #         deserialized_row_data['receptor_razon_social']  # type: ignore
                    # except KeyError:
                    #     logger.fatal(
                    #         "Programming error: referenced field is not in the deserialized "
                    #         "row data.", exc_info=True)
                    #
                    # try:
                    #     tipo_dte = TipoDteEnum(tipo_dte_int)
                    #     dte_data = DteDataL2(
                    #         emisor_rut=emisor_rut,
                    #         tipo_dte=tipo_dte,
                    #         folio=folio,
                    #         fecha_emision_date=fecha_emision_date,
                    #         receptor_rut=receptor_rut,
                    #         monto_total=monto_total,
                    #         emisor_razon_social=emisor_razon_social,
                    #         receptor_razon_social=receptor_razon_social,
                    #         # fecha_vencimiento_date='',
                    #         # firma_documento_dt_naive='',
                    #         # signature_value='',
                    #         # signature_x509_cert_pem='',
                    #         # emisor_giro='',
                    #         # emisor_email='',
                    #         # receptor_email='',
                    #     )
                    #     logger.info("DTE data %s", str(dte_data.as_dict()))
                    #     row_op_return_values = row_op(deserialized_row_data)
                    #     row_op_errors = None
                    # except Exception as exc:
                    #     row_op_return_values = ()
                    #     row_op_errors = str(exc)

                    # try:
                    #     dte_data = input_csv_row_schema.to_dte_data_l2(deserialized_row_data)
                    # except Exception:
                    #     dte_data = None
                    #     logger.exception("Programming error.")
                    #
                    # if dte_data:
                    #     try:
                    #         row_op_return_values = row_op(dte_data)
                    #         row_op_errors = None
                    #     except Exception as exc:
                    #         row_op_return_values = ()
                    #         row_op_errors = str(exc)
                    #         logger.exception("row_op error.")

                    try:
                        row_op_return_values = row_op(input_csv_row_schema, deserialized_row_data)
                        row_op_errors = None
                    except Exception as exc:
                        row_op_return_values = ()
                        row_op_errors = str(exc)
                        logger.exception("FIXME row_op error.")

                # Instead of empty dicts, lists, str, etc, we want to have None.
                validation_errors = validation_errors if validation_errors else None  # type: ignore
                row_op_errors = row_op_errors if row_op_errors else None  # type: ignore

                # Prepare and write output.
                output_row_data = dict(row_data)
                output_row_data.update(dict(
                    row_op_return_values=row_op_return_values,
                    validation_errors=validation_errors,
                    row_op_errors=row_op_errors,
                ))
                csv_writer.writerow(output_row_data)

                # Save errors.
                if validation_errors or row_op_errors:
                    row_error = dict(
                        validation_errors=validation_errors,
                        row_op_errors=row_op_errors,
                    )
                    row_errors.append((row_ix, row_data, row_error))

            # de-indent?
            if row_ix == 0:
                n_rows_proccesed = 0
            else:
                n_rows_proccesed = row_ix - n_rows_offset

    return n_rows_proccesed, row_errors
