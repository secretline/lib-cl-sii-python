.. :changelog:

History
-------

0.6.2 (2019-05-15)
+++++++++++++++++++++++

* (PR #45, 2019-05-15) libs.encoding_utils: improve ``clean_base64``
* (PR #44, 2019-05-15) dte.parse: fix edge case in ``parse_dte_xml``

0.6.1 (2019-05-08)
+++++++++++++++++++++++

* (PR #40, 2019-05-08) dte.data_models: fix bug in ``DteDataL2``

0.6.0 (2019-05-08)
+++++++++++++++++++++++

Includes backwards-incompatible changes to data model ``DteDataL2``.

* (PR #38, 2019-05-08) dte.data_models: alter field ``DteDataL2.signature_x509_cert_pem``
* (PR #37, 2019-05-08) dte.data_models: alter field ``DteDataL2.firma_documento_dt_naive``
* (PR #36, 2019-05-08) libs.crypto_utils: add functions
* (PR #35, 2019-05-07) libs.tz_utils: minor improvements
* (PR #34, 2019-05-06) docs: Fix `bumpversion` command

0.5.1 (2019-05-03)
+++++++++++++++++++++++

* (PR #32, 2019-05-03) Requirements: updates and package upper-bounds

0.5.0 (2019-04-25)
+++++++++++++++++++++++

* (PR #29, 2019-04-25) dte.data_models: modify new fields of ``DteDataL2``
* (PR #28, 2019-04-25) libs: add module ``crypto_utils``
* (PR #27, 2019-04-25) libs: add module ``encoding_utils``
* (PR #26, 2019-04-25) test_data: add files
* (PR #25, 2019-04-25) libs.xml_utils: fix class alias ``XmlElementTree``
* (PR #24, 2019-04-25) requirements: add and update packages
* (PR #22, 2019-04-24) test_data: add files
* (PR #21, 2019-04-22) dte: many improvements
* (PR #20, 2019-04-22) libs.xml_utils: misc improvements
* (PR #19, 2019-04-22) test_data: fix and add real SII DTE & AEC XML files
* (PR #18, 2019-04-22) data.ref: add XML schemas for "Cesion" (RTC)

0.4.0 (2019-04-16)
+++++++++++++++++++++++

* (PR #16, 2019-04-16) dte.parse: change and improve ``clean_dte_xml``
* (PR #14, 2019-04-09) data.ref: merge XML schemas dirs
* (PR #13, 2019-04-09) extras: add Marshmallow field for a DTE's "tipo DTE"

0.3.0 (2019-04-05)
+++++++++++++++++++++++

* (PR #11, 2019-04-05) dte: add module ``parse``
* (PR #10, 2019-04-05) dte: add module ``data_models``
* (PR #9, 2019-04-05) libs: add module ``xml_utils``
* (PR #8, 2019-04-05) add sub-package ``rcv``

0.2.0 (2019-04-04)
+++++++++++++++++++++++

* (PR #6, 2019-04-04) data.ref: add XML schemas of "factura electrónica"
* (PR #5, 2019-04-04) extras: add 'RutField' for Django models, DRF and MM
* (PR #4, 2019-04-04) Config CircleCI

0.1.0 (2019-04-04)
+++++++++++++++++++++++

* (PR #2, 2019-04-04) Add class and constants for RUT
* (PR #1, 2019-04-04) Whole setup for a Python package/library
