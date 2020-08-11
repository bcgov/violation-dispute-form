_includeFile=$(type -p overrides.inc)
if [ ! -z ${_includeFile} ]; then
  . ${_includeFile}
else
  _red='\033[0;31m'; _yellow='\033[1;33m'; _nc='\033[0m'; echo -e \\n"${_red}overrides.inc could not be found on the path.${_nc}\n${_yellow}Please ensure the openshift-developer-tools are installed on and registered on your path.${_nc}\n${_yellow}https://github.com/BCDevOps/openshift-developer-tools${_nc}"; exit 1;
fi

# ================================================================================================================
# Special deployment parameters needed for injecting a user supplied settings into the deployment configuration
# ----------------------------------------------------------------------------------------------------------------

if createOperation; then
  # Ask the user to supply the sensitive parameters ...
  readParameter "DATA_SECURITY_KEY - Please provide the encryption key for the application environment.  If left blank, a 32 character long base64 encoded value will be randomly generated using openssl:" DATA_SECURITY_KEY $(generateKey 32) "false"
  readParameter "RECAPTCHA_SITE_KEY - Please provide reCAPTHCA site key for the application environment.  If left blank, a 48 character long base64 encoded value will be randomly generated using openssl:" RECAPTCHA_SITE_KEY $(generateKey) "false"
  readParameter "RECAPTCHA_SECRET_KEY - Please provide reCAPTHCA secret key for the application environment.  If left blank, a 48 character long base64 encoded value will be randomly generated using openssl:" RECAPTCHA_SECRET_KEY $(generateKey) "false"
  readParameter "OIDC_RP_PROVIDER_ENDPOINT - Please provide the url for the OIDC RP Provider.  The default is a blank string." OIDC_RP_PROVIDER_ENDPOINT "false"
  readParameter "OIDC_RP_CLIENT_SECRET - Please provide the OIDC RP Client Secret.  The default is a blank string." OIDC_RP_CLIENT_SECRET "false"

  # Get the email settings
  readParameter "SMTP_SERVER_ADDRESS - Please provide the address of the outgoing smtp server.  The default is a blank string." SMTP_SERVER_ADDRESS "false"
  readParameter "EMAIL_SERVICE_CLIENT_ID - Please provide the service client id for sending confirmation email.  The default is a blank string." EMAIL_SERVICE_CLIENT_ID "false"
  readParameter "EMAIL_SERVICE_CLIENT_SECRET - Please provide the service client secret to use with above id.  The default is a blank string." EMAIL_SERVICE_CLIENT_SECRET "false"
  readParameter "FEEDBACK_TARGET_EMAIL - Please provide the email address used for recieving application feedback.  The default is a blank string." FEEDBACK_TARGET_EMAIL "false"
  readParameter "SENDER_EMAIL - Please provide the email address used for sending confirmation emails.  The default is a blank string." SENDER_EMAIL "false"
  readParameter "SENDER_NAME - Please provide the name to use with the above email address.  The default is a blank string." SENDER_NAME "false"
else
  # Secrets are removed from the configurations during update operations ...
  printStatusMsg "Update operation detected ...\nSkipping the prompts for DATA_SECURITY_KEY, RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY, OIDC_RP_PROVIDER_ENDPOINT, OIDC_RP_CLIENT_SECRET, SMTP_SERVER_ADDRESS, EMAIL_SERVICE_CLIENT_ID, EMAIL_SERVICE_CLIENT_SECRET, FEEDBACK_TARGET_EMAIL, SENDER_EMAIL, and SENDER_NAME secrets ... \n"
  writeParameter "DATA_SECURITY_KEY" "prompt_skipped" "false"
  writeParameter "RECAPTCHA_SITE_KEY" "prompt_skipped" "false"
  writeParameter "RECAPTCHA_SECRET_KEY" "prompt_skipped" "false"
  writeParameter "OIDC_RP_PROVIDER_ENDPOINT" "prompt_skipped" "false"
  writeParameter "OIDC_RP_CLIENT_SECRET" "prompt_skipped" "false"

  writeParameter "SMTP_SERVER_ADDRESS" "prompt_skipped" "false"
  writeParameter "EMAIL_SERVICE_CLIENT_ID" "prompt_skipped" "false"
  writeParameter "EMAIL_SERVICE_CLIENT_SECRET" "prompt_skipped" "false"
  writeParameter "FEEDBACK_TARGET_EMAIL" "prompt_skipped" "false"
  writeParameter "SENDER_EMAIL" "prompt_skipped" "false"
  writeParameter "SENDER_NAME" "prompt_skipped" "false"
fi

SPECIALDEPLOYPARMS="--param-file=${_overrideParamFile}"
echo ${SPECIALDEPLOYPARMS}