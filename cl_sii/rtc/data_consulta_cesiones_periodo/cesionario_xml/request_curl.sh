curl \
	'https://palena.sii.cl/cgi_rtc/RTC/RTCConsultaCesiones.cgi' \
	-H 'Connection: keep-alive' \
	-H 'Pragma: no-cache' \
	-H 'Cache-Control: no-cache' \
	-H 'Origin: https://palena.sii.cl' \
	-H 'Upgrade-Insecure-Requests: 1' \
	-H 'Content-Type: application/x-www-form-urlencoded' \
	-H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36' \
	-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3' \
	-H 'Referer: https://palena.sii.cl/cgi_rtc/RTC/RTCConsultaCesionesHtml.cgi' \
	-H 'Accept-Encoding: gzip, deflate, br' \
	-H 'Accept-Language: en-US,en;q=0.9,es;q=0.8,es-CL;q=0.7' \
	-H 'Cookie: s_cc=true; NETSCAPE_LIVEWIRE.sec=0000; NETSCAPE_LIVEWIRE.lms=120; NETSCAPE_LIVEWIRE.rut=76389992; NETSCAPE_LIVEWIRE.rutm=76389992; NETSCAPE_LIVEWIRE.dv=6; NETSCAPE_LIVEWIRE.dvm=6; NETSCAPE_LIVEWIRE.clave=SIlZJYNVkGEhMSIKfaS3Z3dwUM; NETSCAPE_LIVEWIRE.mac=1u3350h8h1f73gvthcrmtmju4a; NETSCAPE_LIVEWIRE.exp=20190408130032; TOKEN=4PLG813706VT7; CSESSIONID=4PLG813706VT7; RUT_NS=76389992; DV_NS=6; NETSCAPE_LIVEWIRE.locexp=Mon%2C%2008%20Apr%202019%2017%3A00%3A32%20GMT'
	--data 'TIPOCONSULTA=2&TXTXML=XML&DESDE=04042019&HASTA=08042019' \
	--compressed
