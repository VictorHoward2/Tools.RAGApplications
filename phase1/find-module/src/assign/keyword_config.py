from __future__ import annotations

PIC_BY_MODULE = {
    "OMA": "Nguyen Van A",
    "SKMSAgent": "Do Thi B",
    "SEM": "Tran Van C",
    "SKPM": "Le Van D",
}

FIELD_WEIGHTS = {
    "search_text": 1.2,
    "evidence_text": 1.5,
    "raw_comments": 0.8,
}

LEVEL_WEIGHTS = {
    "strong": 10,
    "medium": 4,
    "weak": 1,
}

MODULE_KEYWORDS = {
    "OMA": {
        "strong": [
            "vtshalsecureelementv1_0targettest",
            "vtshalsecureelementtargettest",
            "secureelementhidltest",
            "ctsomapitestcases",
            "omapi cts",
            "omapi cts applet",
            "com.android.se",
            "secureelementservice",
            "android.se.omapi",
        ],
        "medium": [
            "omapi",
            "vts",
            "cts",
            "secureelement",
            "secure element",
            "channelaccess",
            "apdu",
        ],
        "weak": [
            "ese1",
            "aid",
            "no_such_element_error",
        ],
    },
    "SKMSAgent": {
        "strong": [
            "skmsagent",
            "com.skms.android.agent",
            "samsungseagent",
            "tsmagent",
            "kms agent",
            "skms agent",
            "requested package name",
            "cplc registration",
            "secapploader",
        ],
        "medium": [
            "com.samsung.android.ese",
            "skms",
            "ese agent",
            "kms",
            "playstore",
            "play store",
            "essential security application",
            "system app",
            "preloaded app",
        ],
        "weak": [
            "package info",
            "not compatible at all countries",
            "google team",
        ],
    },
    "SEM": {
        "strong": [
            "semservice",
            "sem daemon",
            "sem_daemon",
            "semfactoryapp",
            "ro.security.esest",
            "ese restricted mode",
            "ese cos",
            "sec_ese_service",
            "sec_ese_cospatch",
            "esecos_daemon",
        ],
        "medium": [
            "sec_ese",
            "nxpesepal",
            "nxp",
            "thales_hal",
            "gemalto_p3",
            "cospatch",
            "eselect response error",
            "select response error",
            "ese_property",
        ],
        "weak": [
            "start close_spi",
            "startspitimer",
            "sw : 6a82",
            "jcop",
        ],
    },
    "SKPM": {
        "strong": [
            " e skpm",
            "skpm    :",
            "skpm:",
            "skpm_hidl_client",
            "skpm_keyinjection",
            "skpm_injectedkeyverification",
            "skpmoperation",
            "vendor.samsung.hardware.security.skpm",
            "key verify error",
            "provisioning fail",
        ],
        "medium": [
            "there is no key file",
            "mbedtls_net_connect",
            "failed, ret : -41",
            "failed, ret : -20",
            "server / port failed",
            "inj error",
            "fido key injection",
            "injectedkeyverification",
            "uaf_asm_status_error",
        ],
        "weak": [
            "pass server response error",
            "authfw",
            "fido",
            "wifi",
            "cellular",
        ],
    },
}

# Một vài rule ưu tiên để resolve overlap
PRIORITY_RULES = [
    {
        "name": "SKPM_direct_log",
        "module": "SKPM",
        "any_keywords": [
            "skpm_keyinjection",
            "skpm_injectedkeyverification",
            "skpm_hidl_client",
            " e skpm",
            "skpm    :",
        ],
        "bonus": 20,
    },
    {
        "name": "OMA_vts_omapi",
        "module": "OMA",
        "any_keywords": [
            "vtshalsecureelementv1_0targettest",
            "vtshalsecureelementtargettest",
            "ctsomapitestcases",
            "omapi cts",
        ],
        "bonus": 18,
    },
    {
        "name": "SKMSAgent_package_or_app",
        "module": "SKMSAgent",
        "any_keywords": [
            "skmsagent",
            "com.skms.android.agent",
            "kms agent",
            "skms agent",
            "requested package name",
        ],
        "bonus": 16,
    },
    {
        "name": "SEM_service_stack",
        "module": "SEM",
        "any_keywords": [
            "sec_ese_service",
            "sec_ese_cospatch",
            "semservice",
            "esecos_daemon",
            "ro.security.esest",
        ],
        "bonus": 16,
    },
]

UNKNOWN_THRESHOLD = 8.0
LOW_CONFIDENCE_GAP = 4.0
HIGH_CONFIDENCE_GAP = 10.0