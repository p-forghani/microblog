# Forgot Password

**User:** clicks on the forgot password link in the login page.<br>
**app:**
1. get the user's email from the request.
2. Check the database to ensure email exists.
3. Generates a forgot password url
4. Send the url to the email.
<br><br>

**User:** Clicks on url in email.<br>
**app:**
1. Shows user a form to enter new password.
2. Get the info and update the password for corresponding email address.
3. Show the user the result of this action.