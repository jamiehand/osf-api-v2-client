from requests.auth import HTTPBasicAuth

# TODO change auth to work with OAuth/tokens instead of basic auth?


DOMAIN = "https://staging2.osf.io/"  # TODO should this variable be called something else?
API_PREFIX = "api/v2/"
URL = "{}{}".format(DOMAIN, API_PREFIX)  # e.g. https://staging2.osf.io/api/v2/

# Change these to a public node id, and the id of a private node that was created by USER1.
PUBLIC_NODE_ID = 'bxsu6'
PRIVATE_NODE_ID = 'p8es7'

# Change these to the email and pw of the main user, who created the private node
USER1 = 'user1@example.com'
PASS1 = 'password1'
AUTH1 = HTTPBasicAuth(USER1, PASS1)
USER1_ID = 'se6py'  # Jamie Hand

# Change these to the email and pw of a second user, who can't see the private node
USER2 = 'user2@example.com'
PASS2 = 'password2'
AUTH2 = HTTPBasicAuth(USER2, PASS2)
USER2_ID = 'cm98x'  # Jamie 2
