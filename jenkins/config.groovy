// Pipeline Configuration Properties
// Import this file into the pipeline using 'load'.
class config {

  // Wait timeout in minutes
  public static final int WAIT_TIMEOUT = 20

  // Deployment configuration
  public static final String[] DEPLOYMENT_ENVIRONMENT_TAGS = ['dev', 'test', 'prod']
  public static final String DEV_ENV = "${DEPLOYMENT_ENVIRONMENT_TAGS[0]}"
  public static final String TEST_ENV = "${DEPLOYMENT_ENVIRONMENT_TAGS[1]}"
  public static final String PROD_ENV = "${DEPLOYMENT_ENVIRONMENT_TAGS[2]}"

  // The name of the project namespace(s).
  public static final String  NAME_SPACE = '069465'

  // Instance Suffix
  public static final String  SUFFIX = ''

  // Apps - Listed in the order they should be tagged
  // Do not deploy schema-spy into prod
  public static final String[] APPS = ['postgresql', 'django', 'schema-spy', 'angular-on-nginx', 'weasyprint', 'backup']
  public static final String[] PROD_APPS = ['postgresql', 'django', 'angular-on-nginx', 'weasyprint', 'backup']
  public static final String SCHEMA_SPY_APP_NAME = "schema-spy"
  
  // Build configuration
  public static final String[] BUILDS = ['angular-on-nginx', 'django']
  
  public static final String[]  WEB_BUILDS = ['nginx-runtime', 'angular-app-build', 'angular-on-nginx-build']
  public static final String  WEB_APP_NAME = "${this.BUILDS[0]}"
  
  public static final String[]  API_BUILDS = ["${this.BUILDS[1]}"]
  public static final String  API_APP_NAME = "${this.BUILDS[1]}"
}

return new config();