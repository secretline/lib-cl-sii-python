"""
Helpers for parsing data from a RTC "Cesiones periodo" XML file.


Usage:

>>> file_path = 'my-data/consulta_cesiones_periodo/CESIONES_60910000-1_2_03312019_02042019.xml'
>>> with open(file_path, mode='rb') as f:
...     g = rtc_cesiones_periodo_xml_processor(f, max_data_rows=None)
...     for row_ix, row_data, deserialized_row_data in g:
...         print(row_ix, row_data, deserialized_row_data)

"""
from datetime import date, datetime
from typing import IO, Iterable, Mapping, Sequence, Tuple

import marshmallow
import marshmallow.fields
import marshmallow.validate

from cl_sii.rut import Rut
from cl_sii.extras import mm_fields
from cl_sii.libs import mm_utils
from cl_sii.libs import xml_utils
from cl_sii.libs.xml_utils import XmlElement


_SII_NS_MAP = {
    'sii': 'http://www.sii.cl/XMLSchema',
}

_EXPECTED_FIELD_NAMES = (
    'CEDENTE',
    'RZ_CEDENTE',
    'MAIL_CEDENTE',
    'CESIONARIO',
    'RZ_CESIONARIO',
    'MAIL_CESIONARIO',
    'MNT_CESION',
    'FCH_CESION',
    'FCH_VENCIMIENTO',
    'ESTADO_CESION',
    'VENDEDOR',
    'DEUDOR',
    'MAIL_DEUDOR',
    'TIPO_DOC',
    'NOMBRE_DOC',
    'FOLIO_DOC',
    'FCH_EMIS_DTE',
    'MNT_TOTAL',
)


def rtc_cesiones_periodo_xml_processor(
    bytes_stream: IO[bytes],
    max_data_rows: int = None,
) -> Iterable[Tuple[int, Mapping[str, object], Mapping[str, object]]]:
    """
    Processor of a RTC "Cesiones periodo" XML file.

    Processing steps:
    - Extract a list of records of "cesión"'s raw data.
    - Instantiate an schema to parse and deserialize each row.
    - For each data row:
        - Using an appropriate schema, deserialize the raw data.
        - Yield the row data before and after deserialization.

    :param bytes_stream: file-like object (binary read mode)
    :param max_data_rows: max number of data rows to process (raise exception if exceeded);
        ``None`` means no limit
    :return: number of data rows processed

    """
    cesion_data_list, _ = extract_cesion_data_list(bytes_stream)
    schema = RtcCesionesPeriodoRowSchema()

    for row_ix, row_data in enumerate(cesion_data_list, start=1):
        if max_data_rows is not None and row_ix > max_data_rows:
            # TODO: custom exception
            raise Exception("Exceeded 'max_data_rows' value: {}.".format(max_data_rows))

        try:
            deserialized_row_data = schema.deserialize_row(row_data)
        except Exception as exc:
            exc_msg = f"Error deserializing 'cesion' item {row_ix} of file: {exc!s}"
            raise Exception(exc_msg) from exc

        yield row_ix, row_data, deserialized_row_data


class RtcCesionesPeriodoRowSchema(marshmallow.Schema):

    EXPECTED_INPUT_FIELDS = tuple(_EXPECTED_FIELD_NAMES)
    EXPECTED_INPUT_FIELDS_STRICT: bool = True

    class Meta:
        strict = True

    ###########################################################################
    # cesion
    ###########################################################################

    cedente_rut = mm_fields.RutField(
        required=True,
        load_from='CEDENTE',
    )
    cedente_razon_social = marshmallow.fields.String(
        required=True,
        load_from='RZ_CEDENTE',
    )
    # note: we would like to use marshmallow field 'Email' but the values are not clean.
    cedente_email = marshmallow.fields.String(
        required=True,
        load_from='MAIL_CEDENTE',
    )

    cesionario_rut = mm_fields.RutField(
        required=True,
        load_from='CESIONARIO',
    )
    cesionario_razon_social = marshmallow.fields.String(
        required=True,
        load_from='RZ_CESIONARIO',
    )
    # note: we would like to use marshmallow field 'Email' but the values are not clean.
    cesionario_email = marshmallow.fields.String(
        required=True,
        load_from='MAIL_CESIONARIO',
    )

    monto = marshmallow.fields.Integer(
        required=True,
        load_from='MNT_CESION',
    )
    fecha_cesion_dt_naive = marshmallow.fields.DateTime(
        format='%Y-%m-%d %H:%M',  # e.g. '2019-04-04 09:09'
        required=True,
        load_from='FCH_CESION',
    )
    fecha_vencimiento_date = mm_utils.CustomMarshmallowDateField(
        format='%Y-%m-%d',  # e.g. '2019-05-01'
        required=True,
        load_from='FCH_VENCIMIENTO',
    )

    ###########################################################################
    # estado cesion
    ###########################################################################

    estado = marshmallow.fields.String(
        required=True,
        load_from='ESTADO_CESION',
    )

    ###########################################################################
    # DTE
    ###########################################################################

    dte_vendedor_rut = mm_fields.RutField(
        required=True,
        load_from='VENDEDOR',
    )
    dte_deudor_rut = mm_fields.RutField(
        required=True,
        load_from='DEUDOR',
    )
    # note: we would like to use marshmallow field 'Email' but the values are not clean.
    dte_deudor_email = marshmallow.fields.String(
        required=True,
        allow_none=True,
        load_from='MAIL_DEUDOR',
    )
    dte_tipo_dte = mm_fields.TipoDteField(
        required=True,
        load_from='TIPO_DOC',
    )
    # e.g. 'Factura Electronica'
    dte_tipo_dte_name = marshmallow.fields.String(
        required=True,
        load_from='NOMBRE_DOC',
    )
    dte_folio = marshmallow.fields.Integer(
        required=True,
        load_from='FOLIO_DOC',
    )
    dte_fecha_emision_date = mm_utils.CustomMarshmallowDateField(
        format='%Y-%m-%d',  # e.g. '2019-04-01'
        required=True,
        load_from='FCH_EMIS_DTE',
    )
    dte_monto_total = marshmallow.fields.Integer(
        required=True,
        load_from='MNT_TOTAL',
    )

    @marshmallow.pre_load
    def preprocess(self, in_data: dict) -> dict:
        # note: required fields checks are run later on automatically thus we may not assume that
        #   values of required fields (`required=True`) exist.

        # Do anything, e.g. set a field's value using a value passed in 'self.context'.

        return in_data

    @marshmallow.post_load
    def postprocess(self, data: dict) -> dict:

        # Do anything, e.g. convert a naive dt to TZ aware.

        return data

    @marshmallow.validates_schema(pass_original=True)
    def validate_schema(self, data: dict, original_data: dict) -> None:
        # Fail validation if there was an unexpected input field.
        unexpected_input_fields = (
            set(original_data)
            - set(self.fields)
            - set(self.EXPECTED_INPUT_FIELDS)
        )
        if unexpected_input_fields:
            if self.EXPECTED_INPUT_FIELDS_STRICT:
                raise marshmallow.ValidationError(
                    'Unexpected input field',
                    field_names=list(unexpected_input_fields))

    # @marshmallow.validates('field_x')
    # def validate_field_x(self, value):
    #     pass

    ###########################################################################
    # non-marshmallow-related methods
    ###########################################################################

    def deserialize_row(self, row: Mapping[str, object]) -> Mapping[str, object]:
        try:
            result = self.load(row)  # type: marshmallow.UnmarshalResult
        except marshmallow.ValidationError as exc:
            exc_msg = "Validation errors during deserialization."
            validation_error_msgs = dict(exc.normalized_messages())
            raise ValueError(exc_msg, validation_error_msgs) from exc

        result_data = result.data  # type: dict
        result_errors = result.errors  # type: dict
        if result_errors:
            raise Exception("Deserialization errors: %s", result_errors)
        return result_data


def extract_cesion_data_list(
    bytes_stream: IO[bytes],
) -> Tuple[Sequence[Mapping[str, str]], Mapping[str, object]]:
    """
    Extract raw data from a RTC "Cesiones periodo" XML file.

    """
    xml_doc = xml_utils.parse_untrusted_xml(bytes_stream.read())

    _resp_hdr_em = xml_doc.find(
        'sii:RESP_HDR',
        namespaces=_SII_NS_MAP)
    _resp_body_em = xml_doc.find(
        'sii:RESP_BODY',
        namespaces=_SII_NS_MAP)

    estado_em = _resp_hdr_em.find(
        'sii:ESTADO',
        namespaces=_SII_NS_MAP)
    glosa_em = _resp_hdr_em.find(
        'sii:GLOSA',
        namespaces=_SII_NS_MAP)
    datos_consulta_em = _resp_body_em.find(
        'DATOS_CONSULTA',
        namespaces=_SII_NS_MAP)
    datos_consulta_rut_em = datos_consulta_em.find(
        'RUT',
        namespaces=_SII_NS_MAP)
    datos_consulta_tipo_consulta_em = datos_consulta_em.find(
        'TIPO_CONSULTA',
        namespaces=_SII_NS_MAP)
    datos_consulta_desde_em = datos_consulta_em.find(
        'DESDE_DDMMAAAA',
        namespaces=_SII_NS_MAP)
    datos_consulta_hasta_em = datos_consulta_em.find(
        'HASTA_DDMMAAAA',
        namespaces=_SII_NS_MAP)

    estado_str = estado_em.text
    # 0
    glosa_str = glosa_em.text
    # (nothing)

    # TODO: raise exception? log error/warning?
    assert (estado_str, glosa_str) == ('0', None)

    cesion_em_list: Sequence[XmlElement] = _resp_body_em.findall(
        'CESION',
        namespaces=_SII_NS_MAP)

    datos_consulta_rut_value = Rut(datos_consulta_rut_em.text.strip())
    datos_consulta_tipo_consulta_str = datos_consulta_tipo_consulta_em.text.strip()

    datos_consulta_desde_str = datos_consulta_desde_em.text.strip()
    datos_consulta_hasta_str = datos_consulta_hasta_em.text.strip()
    # '%d%m%Y' e.g. '04042019'
    datos_consulta_desde_date_value = _parse_date(datos_consulta_desde_str, '%d%m%Y')
    datos_consulta_hasta_date_value = _parse_date(datos_consulta_hasta_str, '%d%m%Y')

    cesion_data_list = [
        {
            cesion_field_em.tag: cesion_field_em.text
            for cesion_field_em in cesion_fields_em.getchildren()
        }
        for cesion_fields_em in cesion_em_list
    ]

    params_consulta = dict(
        datos_consulta_rut=datos_consulta_rut_value,
        datos_consulta_tipo_consulta_str=datos_consulta_tipo_consulta_str,
        datos_consulta_desde_date=datos_consulta_desde_date_value,
        datos_consulta_hasta_date=datos_consulta_hasta_date_value,
    )

    return cesion_data_list, params_consulta


def _parse_date(value: str, date_str_format: str = '%Y-%m-%d') -> date:
    """
    Parse a :class:`date` from a string.

    >>> _parse_date('2019-04-08')
    date(2019, 4, 8)
    >>> _parse_date('04082019', '%d%m%Y')
    date(2019, 4, 8)

    """
    return datetime.strptime(value, date_str_format).date()
