import unittest
from datetime import date, datetime

from cl_sii.dte.data_models import DteDataL1, DteDataL2
from cl_sii.dte.constants import TipoDteEnum
from cl_sii.libs import xml_utils
from cl_sii.rut import Rut

from cl_sii.rtc.data_models_aec import AecXmlCesionData, AecXmlData
from cl_sii.rtc.parse_aec import parse_aec_xml_data, validate_aec_xml


_TEST_AEC_1_FILE_PATH = 'tests/test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2.xml'
_TEST_AEC_2_FILE_PATH = 'tests/test_data/sii-rtc/AEC--76399752-9--33--25568--SEQ-1.xml'
_TEST_AEC_1_DTE_SIGNATURE_VALUE = (
    'fsYP5p/lNfofAz8POShrJjqXdBTNNtvv4/TWCxbvwTIAXr7BLrlvX3C/Hpfo4viqaxSu1OGFgPnk\n'
    'ddDIFwj/ZsVdbdB+MhpKkyha83RxhJpYBVBY3c+y9J6oMfdIdMAYXhEkFw8w63KHyhdf2E9dnbKi\n'
    'wqSxDcYjTT6vXsLPrZk=')
_TEST_AEC_2_DTE_SIGNATURE_VALUE = (
    'wwOMQuFqa6c5gzYSJ5PWfo0OiAf+yNcJK6wx4xJ3VNehlAcMrUB2q+rK/DDhCvjxAoX4NxBACiFD\n'
    'MrTMIfvxrwXjLd1oX37lSFOtsWX6JxL0SV+tLF7qvWCu1Yzw8ypUf7GDkbymJkoTYDF9JFF8kYU4\n'
    'FdU2wttiwne9XH8QFHgXsocKP/aygwiOeGqiNX9o/O5XS2GWpt+KM20jrvtYn7UFMED/3aPacCb1\n'
    'GABizr8mlVEZggZgJunMDChpFQyEigSXMK5I737Ac8D2bw7WB47Wj1WBL3sCFRDlXUXtnMvChBVp\n'
    '0HRUXYuKHyfpCzqIBXygYrIZexxXgOSnKu/yGg==')
_TEST_AEC_1_DTE_X509_CERT = (
    'MIIGVDCCBTygAwIBAgIKMUWmvgAAAAjUHTANBgkqhkiG9w0BAQUFADCB0jELMAkGA1UEBhMCQ0wx\n'
    'HTAbBgNVBAgTFFJlZ2lvbiBNZXRyb3BvbGl0YW5hMREwDwYDVQQHEwhTYW50aWFnbzEUMBIGA1UE\n'
    'ChMLRS1DRVJUQ0hJTEUxIDAeBgNVBAsTF0F1dG9yaWRhZCBDZXJ0aWZpY2Fkb3JhMTAwLgYDVQQD\n'
    'EydFLUNFUlRDSElMRSBDQSBGSVJNQSBFTEVDVFJPTklDQSBTSU1QTEUxJzAlBgkqhkiG9w0BCQEW\n'
    'GHNjbGllbnRlc0BlLWNlcnRjaGlsZS5jbDAeFw0xNzA5MDQyMTExMTJaFw0yMDA5MDMyMTExMTJa\n'
    'MIHXMQswCQYDVQQGEwJDTDEUMBIGA1UECBMLVkFMUEFSQUlTTyAxETAPBgNVBAcTCFF1aWxsb3Rh\n'
    'MS8wLQYDVQQKEyZTZXJ2aWNpb3MgQm9uaWxsYSB5IExvcGV6IHkgQ2lhLiBMdGRhLjEkMCIGA1UE\n'
    'CwwbSW5nZW5pZXLDrWEgeSBDb25zdHJ1Y2Npw7NuMSMwIQYDVQQDExpSYW1vbiBodW1iZXJ0byBM\n'
    'b3BleiAgSmFyYTEjMCEGCSqGSIb3DQEJARYUZW5hY29ubHRkYUBnbWFpbC5jb20wgZ8wDQYJKoZI\n'
    'hvcNAQEBBQADgY0AMIGJAoGBAKQeAbNDqfi9M2v86RUGAYgq1ZSDioFC6OLr0SwiOaYnLsSOl+Kx\n'
    'O394PVwSGa6rZk1ErIZonyi15fU/0nHZLi8iHLB49EB5G3tCwh0s8NfqR9ck0/3Z+TXhVUdiJyJC\n'
    '/z8x5I5lSUfzNEedJRidVvp6jVGr7P/SfoEfQQTLP3mBAgMBAAGjggKnMIICozA9BgkrBgEEAYI3\n'
    'FQcEMDAuBiYrBgEEAYI3FQiC3IMvhZOMZoXVnReC4twnge/sPGGBy54UhqiCWAIBZAIBBDAdBgNV\n'
    'HQ4EFgQU1dVHhF0UVe7RXIz4cjl3/Vew+qowCwYDVR0PBAQDAgTwMB8GA1UdIwQYMBaAFHjhPp/S\n'
    'ErN6PI3NMA5Ts0MpB7NVMD4GA1UdHwQ3MDUwM6AxoC+GLWh0dHA6Ly9jcmwuZS1jZXJ0Y2hpbGUu\n'
    'Y2wvZWNlcnRjaGlsZWNhRkVTLmNybDA6BggrBgEFBQcBAQQuMCwwKgYIKwYBBQUHMAGGHmh0dHA6\n'
    'Ly9vY3NwLmVjZXJ0Y2hpbGUuY2wvb2NzcDAjBgNVHREEHDAaoBgGCCsGAQQBwQEBoAwWCjEzMTg1\n'
    'MDk1LTYwIwYDVR0SBBwwGqAYBggrBgEEAcEBAqAMFgo5NjkyODE4MC01MIIBTQYDVR0gBIIBRDCC\n'
    'AUAwggE8BggrBgEEAcNSBTCCAS4wLQYIKwYBBQUHAgEWIWh0dHA6Ly93d3cuZS1jZXJ0Y2hpbGUu\n'
    'Y2wvQ1BTLmh0bTCB/AYIKwYBBQUHAgIwge8egewAQwBlAHIAdABpAGYAaQBjAGEAZABvACAARgBp\n'
    'AHIAbQBhACAAUwBpAG0AcABsAGUALgAgAEgAYQAgAHMAaQBkAG8AIAB2AGEAbABpAGQAYQBkAG8A\n'
    'IABlAG4AIABmAG8AcgBtAGEAIABwAHIAZQBzAGUAbgBjAGkAYQBsACwAIABxAHUAZQBkAGEAbgBk\n'
    'AG8AIABoAGEAYgBpAGwAaQB0AGEAZABvACAAZQBsACAAQwBlAHIAdABpAGYAaQBjAGEAZABvACAA\n'
    'cABhAHIAYQAgAHUAcwBvACAAdAByAGkAYgB1AHQAYQByAGkAbzANBgkqhkiG9w0BAQUFAAOCAQEA\n'
    'mxtPpXWslwI0+uJbyuS9s/S3/Vs0imn758xMU8t4BHUd+OlMdNAMQI1G2+q/OugdLQ/a9Sg3clKD\n'
    'qXR4lHGl8d/Yq4yoJzDD3Ceez8qenY3JwGUhPzw9oDpg4mXWvxQDXSFeW/u/BgdadhfGnpwx61Un\n'
    '+/fU24ZgU1dDJ4GKj5oIPHUIjmoSBhnstEhIr6GJWSTcDKTyzRdqBlaVhenH2Qs6Mw6FrOvRPuud\n'
    'B7lo1+OgxMb/Gjyu6XnEaPu7Vq4XlLYMoCD2xrV7WEADaDTm7KcNLczVAYqWSF1WUqYSxmPoQDFY\n'
    '+kMTThJyCXBlE0NADInrkwWgLLygkKI7zXkwaw==')
_TEST_AEC_2_DTE_X509_CERT = (
    'MIIF/zCCBOegAwIBAgICMhQwDQYJKoZIhvcNAQELBQAwgaYxCzAJBgNVBAYTAkNMMRgwFgYDVQQK\n'
    'Ew9BY2VwdGEuY29tIFMuQS4xSDBGBgNVBAMTP0FjZXB0YS5jb20gQXV0b3JpZGFkIENlcnRpZmlj\n'
    'YWRvcmEgQ2xhc2UgMiBQZXJzb25hIE5hdHVyYWwgLSBHNDEeMBwGCSqGSIb3DQEJARYPaW5mb0Bh\n'
    'Y2VwdGEuY29tMRMwEQYDVQQFEwo5NjkxOTA1MC04MB4XDTE3MDEwNjE0MDI1NFoXDTIwMDEwNjE0\n'
    'MDI1NFowgY8xCzAJBgNVBAYTAkNMMRgwFgYDVQQMEw9QRVJTT05BIE5BVFVSQUwxIzAhBgNVBAMT\n'
    'GkdJQU5JTkEgQkVMRU4gRElBWiBVUlJVVElBMSwwKgYJKoZIhvcNAQkBFh1kYW5pZWwuYXJhdmVu\n'
    'YUBpbm5vdmFtb2JlbC5jbDETMBEGA1UEBRMKMTY0Nzc3NTItOTCCASIwDQYJKoZIhvcNAQEBBQAD\n'
    'ggEPADCCAQoCggEBANLQYWfXROtuPiyInyROQc+DZ2LdpvaShxU6iU2xB+CQs74HZ+oS1BINzmL1\n'
    'g9oY7hHvT+/H+hucOlN7xomH/UuDikjoySjhbH3xBMzh6qWHvDqcfTswYuHES2hO9keTzwytyUIP\n'
    'HTctMNJ32mIQ/fGU8H+Qf7adtV+A7k3jXgvCu3DQ5ceeR1xUyDbTXIWJDtg215sa3YSkto3iPNSh\n'
    'qiKeGfsh/qUEaH3oK/Tf0lOG/CG/bnvLdubacc9o7B5QS6JF5ILMffCEuzBrxyMZLhBQYm1ah6dS\n'
    'EbCsDNkc6sQMHLYg/0qG1N+cILXVyusGGCCEDTfmXb/AI4rEKaJt0XMCAwEAAaOCAkowggJGMB8G\n'
    'A1UdIwQYMBaAFGWlqz4/yLZRbRF+X8MKB+ZDoAi2MB0GA1UdDgQWBBSHoSD4nd2UJuwzmJnJud0L\n'
    'WSO+MzALBgNVHQ8EBAMCBPAwHQYDVR0lBBYwFAYIKwYBBQUHAwIGCCsGAQUFBwMEMBEGCWCGSAGG\n'
    '+EIBAQQEAwIFoDB1BgNVHSAEbjBsMGoGCCsGAQQBtWsCMF4wMQYIKwYBBQUHAgEWJWh0dHBzOi8v\n'
    'YWNnNC5hY2VwdGEuY29tL0NQUy1BY2VwdGFjb20wKQYIKwYBBQUHAgIwHTAWFg9BY2VwdGEuY29t\n'
    'IFMuQS4wAwIBCRoDVEJEMFoGA1UdEgRTMFGgGAYIKwYBBAHBAQKgDBYKOTY5MTkwNTAtOKAkBggr\n'
    'BgEFBQcIA6AYMBYMCjk2OTE5MDUwLTgGCCsGAQQBwQECgQ9pbmZvQGFjZXB0YS5jb20waAYDVR0R\n'
    'BGEwX6AYBggrBgEEAcEBAaAMFgoxNjQ3Nzc1Mi05oCQGCCsGAQUFBwgDoBgwFgwKMTY0Nzc3NTIt\n'
    'OQYIKwYBBAHBAQKBHWRhbmllbC5hcmF2ZW5hQGlubm92YW1vYmVsLmNsMEcGCCsGAQUFBwEBBDsw\n'
    'OTA3BggrBgEFBQcwAYYraHR0cHM6Ly9hY2c0LmFjZXB0YS5jb20vYWNnNC9vY3NwL0NsYXNlMi1H\n'
    'NDA/BgNVHR8EODA2MDSgMqAwhi5odHRwczovL2FjZzQuYWNlcHRhLmNvbS9hY2c0L2NybC9DbGFz\n'
    'ZTItRzQuY3JsMA0GCSqGSIb3DQEBCwUAA4IBAQCx+mdIdIu1QQf6mnFDCYfcyhU5t5iKV+8Pr8LV\n'
    'WZdlwGmKRbzhqYKZ8oo5Bfmto105z7JYJIFyZiny/8sb9IcoPLNG/6LtWZZFmHkZabC9sUEjSxU/\n'
    'w8w2VMhrCILonVjnhLX8VHNMkc3Xy17JgvUAIcor2MHfNxn0lyEM3EZdROkgDxwuWfS388mqg8KB\n'
    'B/QNi7AB5U9kB7M5wfGr2lYAvkzlTmHlcBFI2fI6odZlfzLnyKN/ow9mow4Z4ngKuhlTpTUVrACg\n'
    'jhl1gijANMhS1SwNpPgOLlf54KbXTQxWrrwt9mEMZBH7w6imtxJGzNWPjPcykRB7YQxhrHkfzmrw')


class OthersTest(unittest.TestCase):

    def test_AEC_XML_SCHEMA_OBJ(self):
        pass


class FunctionsTest(unittest.TestCase):

    def test_validate_aec_xml_ok_1(self) -> None:
        with open(_TEST_AEC_1_FILE_PATH, mode='rb') as f:
            xml_doc_1 = xml_utils.parse_untrusted_xml(f.read())

        self.assertIsNone(validate_aec_xml(xml_doc_1))

    def test_validate_aec_xml_ok_2(self) -> None:
        with open(_TEST_AEC_2_FILE_PATH, mode='rb') as f:
            xml_doc_2 = xml_utils.parse_untrusted_xml(f.read())

        self.assertIsNone(validate_aec_xml(xml_doc_2))

    def test_validate_aec_xml_fail(self) -> None:
        # TODO: implement for 'validate_aec_xml'
        pass

    def test_parse_aec_xml_data_ok_1(self) -> None:
        # TODO: split in separate tests, with more coverage.

        with open(_TEST_AEC_1_FILE_PATH, mode='rb') as f:
            xml_doc = xml_utils.parse_untrusted_xml(f.read())
        aec_xml = parse_aec_xml_data(xml_doc)

        expected = AecXmlData(
            dte=DteDataL2(
                emisor_rut=Rut('76354771-K'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=170,
                fecha_emision_date=date(2019, 4, 1),
                receptor_rut=Rut('96790240-3'),
                monto_total=2996301,
                emisor_razon_social='INGENIERIA ENACON SPA',
                receptor_razon_social='MINERA LOS PELAMBRES',
                fecha_vencimiento_date=None,
                firma_documento_dt_naive=datetime(2019, 4, 1, 1, 36, 40),
                signature_value_base64=_TEST_AEC_1_DTE_SIGNATURE_VALUE,
                signature_x509_cert_base64=_TEST_AEC_1_DTE_X509_CERT,
                emisor_giro='Ingenieria y Construccion',
                emisor_email='ENACONLTDA@GMAIL.COM',
                receptor_email=None,
            ),
            cedente_rut=Rut('76389992-6'),
            cesionario_rut=Rut('76598556-0'),
            fecha_firma_dt_naive=datetime(2019, 4, 5, 12, 57, 32),
            cesiones=[
                AecXmlCesionData(
                    dte=DteDataL1(
                        emisor_rut=Rut('76354771-K'),
                        tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                        folio=170,
                        fecha_emision_date=date(2019, 4, 1),
                        receptor_rut=Rut('96790240-3'),
                        monto_total=2996301,
                    ),
                    seq=1,
                    cedente_rut=Rut('76354771-K'),
                    cesionario_rut=Rut('76389992-6'),
                    monto=2996301,
                    fecha_cesion_dt_naive=datetime(2019, 4, 1, 10, 22, 2),
                    ultimo_vencimiento_date=date(2019, 5, 1),
                    cedente_razon_social='SERVICIOS BONILLA Y LOPEZ Y COMPAÑIA LIMITADA',
                    cedente_direccion='MERCED 753  16 ARBOLEDA DE QUIILOTA',
                    cedente_email='enaconltda@gmail.com',
                    cesionario_razon_social='ST CAPITAL S.A.',
                    cesionario_direccion='Isidora Goyenechea 2939 Oficina 602',
                    cesionario_email='fynpal-app-notif-st-capital@fynpal.com',
                    dte_deudor_email=None,
                    cedente_declaracion_jurada=(
                        'Se declara bajo juramento que SERVICIOS BONILLA Y LOPEZ Y COMPAÑIA '
                        'LIMITADA, RUT 76354771-K ha puesto a disposición del cesionario ST '
                        'CAPITAL S.A., RUT 76389992-6, el o los documentos donde constan los '
                        'recibos de las mercaderías entregadas o servicios prestados, entregados '
                        'por parte del deudor de la factura MINERA LOS PELAMBRES, RUT 96790240-3, '
                        'deacuerdo a lo establecido en la Ley N°19.983.'
                    ),
                ),
                AecXmlCesionData(
                    dte=DteDataL1(
                        emisor_rut=Rut('76354771-K'),
                        tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                        folio=170,
                        fecha_emision_date=date(2019, 4, 1),
                        receptor_rut=Rut('96790240-3'),
                        monto_total=2996301,
                    ),
                    seq=2,
                    cedente_rut=Rut('76389992-6'),
                    cesionario_rut=Rut('76598556-0'),
                    monto=2996301,
                    fecha_cesion_dt_naive=datetime(2019, 4, 5, 12, 57, 32),
                    ultimo_vencimiento_date=date(2019, 5, 1),
                    cedente_razon_social='ST CAPITAL S.A.',
                    cedente_direccion='Isidora Goyenechea 2939 Oficina 602',
                    cedente_email='APrat@Financiaenlinea.com',
                    cesionario_razon_social='Fondo de Inversión Privado Deuda y Facturas',
                    cesionario_direccion='Arrayan 2750 Oficina 703 Providencia',
                    cesionario_email='solicitudes@stcapital.cl',
                    dte_deudor_email=None,
                    cedente_declaracion_jurada=(
                        'Se declara bajo juramento que ST CAPITAL S.A., RUT 76389992-6 ha puesto '
                        'a disposicion del cesionario Fondo de Inversión Privado Deuda y Facturas, '
                        'RUT 76598556-0, el documento validamente emitido al deudor MINERA LOS '
                        'PELAMBRES, RUT 96790240-3.'
                    ),
                ),
            ],
            contacto_nombre='ST Capital Servicios Financieros',
            contacto_telefono=None,
            contacto_email='APrat@Financiaenlinea.com',
        )

        self.assertEqual(aec_xml, expected)

    def test_parse_aec_xml_data_ok_2(self) -> None:
        # TODO: split in separate tests, with more coverage.

        with open(_TEST_AEC_2_FILE_PATH, mode='rb') as f:
            xml_doc = xml_utils.parse_untrusted_xml(f.read())
        aec_xml = parse_aec_xml_data(xml_doc)

        expected = AecXmlData(
            dte=DteDataL2(
                emisor_rut=Rut('76399752-9'),
                tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                folio=25568,
                fecha_emision_date=date(2019, 3, 29),
                receptor_rut=Rut('96874030-K'),
                monto_total=230992,
                emisor_razon_social='COMERCIALIZADORA INNOVA MOBEL SPA',
                receptor_razon_social='EMPRESAS LA POLAR S.A.',
                fecha_vencimiento_date=None,
                firma_documento_dt_naive=datetime(2019, 3, 28, 13, 59, 52),
                signature_value_base64=_TEST_AEC_2_DTE_SIGNATURE_VALUE,
                signature_x509_cert_base64=_TEST_AEC_2_DTE_X509_CERT,
                emisor_giro='COMERCIALIZACION DE PRODUCTOS PARA EL HOGAR',
                emisor_email='ANGEL.PEZO@APCASESORIAS.CL',
                receptor_email=None,
            ),
            cedente_rut=Rut('76399752-9'),
            cesionario_rut=Rut('76389992-6'),
            fecha_firma_dt_naive=datetime(2019, 4, 4, 9, 9, 52),
            cesiones=[
                AecXmlCesionData(
                    dte=DteDataL1(
                        emisor_rut=Rut('76399752-9'),
                        tipo_dte=TipoDteEnum.FACTURA_ELECTRONICA,
                        folio=25568,
                        fecha_emision_date=date(2019, 3, 29),
                        receptor_rut=Rut('96874030-K'),
                        monto_total=230992,
                    ),
                    seq=1,
                    cedente_rut=Rut('76399752-9'),
                    cesionario_rut=Rut('76389992-6'),
                    monto=230992,
                    fecha_cesion_dt_naive=datetime(2019, 4, 4, 9, 9, 52),
                    ultimo_vencimiento_date=date(2019, 4, 28),
                    cedente_razon_social='COMERCIALIZADORA INNOVA MOBEL SPA',
                    cedente_direccion='LOS CIPRESES 2834',
                    cedente_email='camilo.perez@innovamobel.cl',
                    cesionario_razon_social='ST CAPITAL S.A.',
                    cesionario_direccion='Isidora Goyenechea 2939 Oficina 602',
                    cesionario_email='fynpal-app-notif-st-capital@fynpal.com',
                    dte_deudor_email=None,
                    cedente_declaracion_jurada=(
                        'Se declara bajo juramento que COMERCIALIZADORA INNOVA MOBEL SPA, RUT '
                        '76399752-9 ha puesto a disposición del cesionario ST CAPITAL S.A., RUT '
                        '76389992-6, el o los documentos donde constan los recibos de las '
                        'mercaderías entregadas o servicios prestados, entregados por parte del '
                        'deudor de la factura EMPRESAS LA POLAR S.A., RUT 96874030-K, deacuerdo a '
                        'lo establecido en la Ley N°19.983.')
                ),
            ],
            contacto_nombre=None,
            contacto_telefono=None,
            contacto_email='fynpal-app-notif-st-capital@fynpal.com',
        )

        self.assertEqual(aec_xml, expected)
