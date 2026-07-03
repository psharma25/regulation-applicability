# Acme Corp information security policy (sample document)

## Access control
All employees must use multi-factor authentication (MFA) for email, VPN,
and any system containing customer data. Hardware security keys are required
for administrators. Passwords must be at least 14 characters and rotated
only upon suspected compromise.

## Incident response
Suspected security incidents must be reported to the security team within
1 hour of discovery via the #sec-incident channel or the 24/7 hotline.
The incident commander classifies severity (SEV1-SEV4) within 30 minutes.
SEV1 incidents require executive notification within 2 hours and customer
notification within 72 hours where legally required (e.g., GDPR).

## Data handling
Customer data is classified as Confidential. It may not be copied to
personal devices or third-party AI tools without a signed DPA and security
review. Production data may not be used in test environments unless
anonymized.

## Vendor security
Vendors handling Confidential data must complete a security questionnaire,
hold SOC 2 Type II or ISO 27001 certification, and agree to breach
notification within 24 hours.
