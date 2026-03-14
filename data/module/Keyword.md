Cách phân loại issue (OMA, SKMSAgent, SEM, SKPM)

Để phân loại xem issue thuộc về module nào, chúng ta dựa vào các keyword hay xuất hiện trong các thông tin được cung cấp của Issue (title, description, log, ...). 
Hiện tại chúng ta chỉ quan tâm đến 4 module chính: OMA, SKMSAgent, SEM, SKPM.
3 module OMA, SKMSAgent, SEM có làm việc với bên app bên thứ 3. Còn module SKPM thì độc lập với app bên thứ 3.

Dưới đây là một số keyword phổ biến được sử dụng để phân loại issue vào các module tương ứng:
---

OMA:

- CTS (testcase fail):
  - CtsOmapiTestCases
  - CtsSecureElementAccessControlTestCases1
  - CtsSecureElementAccessControlTestCases2
  - CtsSecureElementAccessControlTestCases3

- VTS (testcase fail):
  - VtsHalSecureElementTargetTest 
  - VtsHalSecureElementV1_0TargetTest 
- com.android.se package 
- Error when install OMAPI CTS Applet
- SecureElementApplication/SecureElementService/SEService apps/services
- Log:
  - SecureElement
  - secure-element
- OMAPI CTS application

---

SKMSAgent	
- Security feature:
  - SEC_PRODUCT_FEATURE_SECURITY_SUPPORT_CNSKMS
  - SEC_PRODUCT_FEATURE_SECURITY_CONFIG_MSG_VERSION
- SKMSAgent package:
  - com.skms.android.agent
  - com.samsung.android.ese
- SKMSAgent, SamsungSeAgent
- eSE util application (eSE clear, key rotation check, key rotation, change URL, get   - CPLC, sec applet loader (SecAppLoader))
- CPLC registration
- Log:
  - SKMSAgent/SamsungSeAgent
  - TSMAgent
  - SEC_ESE
  - (Sometime) NXP/THALES_HAL/GEMALTO_P3/SemService

---

SEM	
- ESES/ESEA
- Security feature:
  - SEC_PRODUCT_FEATURE_SECURITY_SUPPORT_ESE_REE_SPI
  - SEC_PRODUCT_FEATURE_SECURITY_CONFIG_ESE_CHIP_VENDOR
  - SEC_PRODUCT_FEATURE_SECURITY_CONFIG_ESE_COS_NAME
  - SEC_PRODUCT_FEATURE_SECURITY_SUPPORT_ESEK
- eSE HAL/SEMFactoryApp/sem_daemon/SEMService/SEM HAL apps
- eSE
- eSE restricted mode
- Ap-eSE
- eSE COS
- Bringup (SW PL request check bringup của SEM/eSE state trên 1 project)
- Log:
  - ro.security.esest/ro.security.esebap
  - SEC_ESE
  - SEM
  - NXP/THALES_HAL/GEMALTO_P3
  - (Sometime) SecureElement
- (Sometime) CTS, VTS tương tự như OMA

---

SKPM	
- Trong log có keyword "SKPM" hoặc "skpm", ví dụ:
  - 01-25 08:16:46.003  1000 10289 26262 E SKPM    : failed to write file, errno = 28,   - error str = No space left on device
  - 11-14 15:28:21.081  1000  9849  9862 E SKPM    : skpm_keyInjection is failed, ret :   - -55
  - 09-22 13:24:15.559 W 1000 459 4926 libc Unable to set property "ctl.interface_start"   - to "aidl/vendor.samsung.hardware.security.skpm.ISehSkpm/default":   - PROP_ERROR_HANDLE_CONTROL_MESSAGE (0x20)
  - ...

- Trong phần coBringup (SW PL request check bringup của SKPM state trên 1 project)

---