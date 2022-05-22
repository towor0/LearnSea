# LearnSea
User generated learning platform

# How to setup
1. go to shell and open python (type "python" or "python3")
2. import database by typing "from main import db"
3. create the database by typing "db.create_all()"

# Setting up admin account
1. go to shell and open python (type "python" or "python3")
2. import database and User class by typing "from main import db, User"
3. after creating your user account on LearnSea you can find it by typing "myUser = User.query.filter_by(username='YOURUSERNAME').first()"
4. now you have to set the role of the account to admin by typing "myUser.role = 'admin'"
5. after the role is set to admin you can access the "/admin" page
