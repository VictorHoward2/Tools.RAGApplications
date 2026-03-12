Modules Overview
    Terminology
        Secure Element: Smart chip manages and stores information securely, isolated from the rest of the device (hardware isolation).
        SD (Security Domain): Trong chip Secure Element, nó được chia ra các phân vùng nhỏ, gọi là SD.
        Applet: Applet được chứa trong SD, nó có vai trò lưu trữ thông tin.
    Modules:
        OMA (Open Mobile API): It is an AOSP (Android Open Source Project). It is a communication standard that allows android applications to access eSE.
        Samsung eSE API (SKMSAgent - Samsung Key Management System Agent): Basically eSE SDK allows client application to communicate with eSE. Also eSE SDK act as proxy application between SKMS server and eSE. From now on, I will use the name SKMSAgent.
        SEM (Secure Element Manage): Located behind SKMSAgent, it provides additional security features to ensure transactions to eSE are conducted correctly.
        SKPM (Samsung Key Provisioning Mamagement): A mechanism that allows key injection from the server to an application that needs it.