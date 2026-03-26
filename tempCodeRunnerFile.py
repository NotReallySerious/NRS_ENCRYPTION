import string

def password_generate_policy(x):
    
    letters_uppercase = list(string.ascii_uppercase)
    letters_lowercase = list(string.ascii_lowercase)
    numbers = list(string.digits)
    special_chars = list(string.punctuation)

    min_length = 12
    uppercase_count = 0
    lowercase_count = 0
    number_count = 0
    special_count = 0
    all_good = True

    while all_good is True:
        if len(x) < 12:
            return False

        for char in x:
            if char in letters_lowercase:
                lowercase_count += 1
            elif char in letters_uppercase:
                uppercase_count += 1
            elif char in numbers:
                number_count += 1
            elif char in special_chars:
                special_count += 1
            else:
                return False

        if lowercase_count < 1:
            print('Password must have at least 1 lowercase')
            all_good = False
        elif uppercase_count < 1:
            print('Password must have at least 1 uppercase')
            all_good = False
        elif number_count < 1:
            print('Password must have at least 1 digit number')
            all_good = False
        elif special_count < 1:
            print('Password must have at least 1 special character')
            all_good = False
        
    if all_good:
        print(f"{x} is matched all criterias. Proceeding")

password_generate_policy('MyPAsswordIsSoStrong123!_')