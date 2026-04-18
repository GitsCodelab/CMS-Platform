# LDAP User Store Configuration

This guide explains how to configure LDAP/Active Directory as a user store in WSO2 Identity Server.

## Prerequisites

- WSO2 IS 7.0.0 running
- Access to LDAP/Active Directory server
- LDAP connection details (URL, DN, password)
- Admin credentials for WSO2 IS

## Configuration Steps

### Step 1: Enable LDAP in Environment

Edit `.env`:
```env
LDAP_ENABLED=true
LDAP_URL=ldap://ldap-server:389
LDAP_DN=cn=admin,dc=example,dc=com
LDAP_PASSWORD=your_ldap_password
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
```

### Step 2: Access Admin Console

1. Navigate to: https://localhost:9443/carbon
2. Login with admin credentials
3. Go to: Main → User Management → User Stores

### Step 3: Add LDAP User Store

Click **Add User Store** and configure:

```
Domain Name: LDAP
Description: LDAP User Store
Type: LDAP
```

### Step 4: LDAP Connection Properties

Configure the following properties:

```
CONNECTION_NAME=LDAP Connection
CONNECTION_URL=ldap://ldap-server:389
CONNECTION_NAME=cn=admin,dc=example,dc=com
CONNECTION_PASSWORD=password
BASE_DN=dc=example,dc=com
REFERRAL=follow
BACKLINKS=false
CACHE_ENABLED=true
CACHE_TTL=900000
```

### Step 5: LDAP User Configuration

```
USER_SEARCH_BASE=ou=users,dc=example,dc=com
USER_ENTRY_OBJECT_CLASS=inetOrgPerson
USER_NAME_ATTRIBUTE=uid
USER_NAME_SEARCH_FILTER=(&(objectClass=inetOrgPerson)(uid=?))
USER_NAME_LIST_FILTER=(&(objectClass=inetOrgPerson)(uid=*))
DISPLAY_NAME_ATTRIBUTE=displayName
EMAIL_ATTRIBUTE=mail
MOBILE_ATTRIBUTE=mobile
USER_ENABLED_ATTRIBUTE=userAccountControl
```

### Step 6: LDAP Group Configuration

```
GROUP_SEARCH_BASE=ou=groups,dc=example,dc=com
GROUP_ENTRY_OBJECT_CLASS=groupOfNames
GROUP_NAME_ATTRIBUTE=cn
GROUP_NAME_SEARCH_FILTER=(&(objectClass=groupOfNames)(cn=?))
GROUP_NAME_LIST_FILTER=(&(objectClass=groupOfNames)(cn=*))
MEMBER_ATTRIBUTE=member
MEMBER_OF_ATTRIBUTE=memberOf
```

### Step 7: Test Connection

1. Click **Test Connection**
2. Enter test username and password
3. Verify connection is successful

### Step 8: Save Configuration

Click **Update** to save the configuration.

## User Synchronization

### Manual Sync

```bash
# SSH into IS container
docker compose exec cms-wso2is bash

# Navigate to bin directory
cd /home/wso2carbon/wso2is-7.0.0/bin

# Run sync command
./sync-ldap-users.sh
```

### Automatic Sync

Configure in `carbon.xml`:
```xml
<UserStoreManager>
    <SyncInterval>3600</SyncInterval>
    <SyncMode>sync</SyncMode>
</UserStoreManager>
```

## Troubleshooting

### Connection Failed

**Error:** "Unable to connect to LDAP server"

**Solution:**
1. Verify LDAP server is running
2. Check LDAP URL and port
3. Verify firewall allows connection
4. Test with LDAP client:
   ```bash
   ldapsearch -H ldap://ldap-server:389 -x -D "cn=admin,dc=example,dc=com" -W
   ```

### User Not Found

**Error:** "User not found in LDAP"

**Solution:**
1. Verify USER_SEARCH_BASE is correct
2. Check USER_NAME_SEARCH_FILTER matches LDAP structure
3. Verify user exists in LDAP:
   ```bash
   ldapsearch -H ldap://ldap-server:389 -x -b "ou=users,dc=example,dc=com" "uid=username"
   ```

### Slow User Lookup

**Error:** LDAP queries taking too long

**Solution:**
1. Enable caching: `CACHE_ENABLED=true`
2. Adjust cache TTL: `CACHE_TTL=900000`
3. Optimize search filters
4. Check LDAP server performance

## Active Directory Specific

### Connection String for AD

```
CONNECTION_URL=ldap://domain.com:389
CONNECTION_NAME=domain\username
BASE_DN=dc=domain,dc=com
```

### User Attributes for AD

```
USER_NAME_ATTRIBUTE=sAMAccountName
DISPLAY_NAME_ATTRIBUTE=displayName
EMAIL_ATTRIBUTE=mail
MOBILE_ATTRIBUTE=telephoneNumber
USER_ENABLED_ATTRIBUTE=userAccountControl
```

### Group Search for AD

```
GROUP_SEARCH_BASE=cn=Users,dc=domain,dc=com
GROUP_ENTRY_OBJECT_CLASS=group
GROUP_NAME_ATTRIBUTE=cn
MEMBER_ATTRIBUTE=member
```

## Testing LDAP Integration

### Create Test User in LDAP

```ldif
dn: uid=testuser,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: testuser
cn: Test User
sn: User
userPassword: password123
mail: testuser@example.com
```

### Test Login

1. Access account portal: https://localhost:9443/accountportal
2. Enter LDAP username and password
3. Verify successful login

### Test API Access

```bash
# Get token
curl -X POST https://localhost:9443/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=testuser&password=password123&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&scope=openid profile email"

# Access protected resource
curl -X GET https://localhost:9443/api/me \
  -H "Authorization: Bearer $TOKEN"
```

## Performance Tuning

### Caching Configuration

```xml
<UserStoreManager>
    <CacheEnabled>true</CacheEnabled>
    <CacheTTL>900000</CacheTTL>
    <CacheSize>5000</CacheSize>
    <MaxUserCount>10000</MaxUserCount>
</UserStoreManager>
```

### Connection Pool

```xml
<ConnectionPool>
    <MaxActive>50</MaxActive>
    <MaxIdle>5</MaxIdle>
    <MaxWait>30000</MaxWait>
</ConnectionPool>
```

### Batch Operations

```xml
<BatchSize>1000</BatchSize>
```

## Migration from Local to LDAP

### Step 1: Export Existing Users

```bash
# Export from WSO2 database
docker compose exec cms-wso2is mysql -u root -p wso2is < export_users.sql
```

### Step 2: Import to LDAP

Create LDIF file with exported users and import:
```bash
ldapadd -H ldap://ldap-server:389 -D "cn=admin,dc=example,dc=com" -W -f users.ldif
```

### Step 3: Enable LDAP in WSO2 IS

Configure as described above.

### Step 4: Test and Verify

1. Test user login with LDAP credentials
2. Verify all users can authenticate
3. Check group memberships

## Useful Commands

```bash
# Test LDAP connection
ldapsearch -H ldap://ldap-server:389 -x -b "dc=example,dc=com" -W

# List all users
ldapsearch -H ldap://ldap-server:389 -x -b "ou=users,dc=example,dc=com" "objectClass=inetOrgPerson"

# List specific user
ldapsearch -H ldap://ldap-server:389 -x -b "dc=example,dc=com" "uid=username"

# Modify user password
ldappasswd -H ldap://ldap-server:389 -x -D "cn=admin,dc=example,dc=com" -W "uid=username,ou=users,dc=example,dc=com"
```

## Security Considerations

- Use LDAPS (LDAP over SSL) for production: `ldaps://ldap-server:636`
- Change default admin credentials
- Use service accounts with minimal permissions
- Enable audit logging
- Implement rate limiting
- Use firewall to restrict access
- Encrypt LDAP passwords in transit

---

**Last Updated:** April 2026
**Version:** WSO2 IS 7.0.0
**Status:** Production Ready
