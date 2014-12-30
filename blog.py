import web
import hashlib
import model

# URL Mapping
urls = ('/', 'index',
        '/view/(\d+)', 'View',
        '/signup', 'signup',
        '/welcome', 'welcome',
        '/new', 'New',
        '/delete/(\d+)', 'Delete',
        '/edit/(\d+)', 'Edit',
        '/login', 'login',
        '/logout', 'logout')

# Templates
t_globals = {
    'datestr': web.datestr
}
render = web.template.render('templates', globals=t_globals)


#test DB created under Win7 for User Authentication
db = web.database(dbn='mysql', user='python', pw='', db='testdb') 

#for redirection:
#raise web.seeother('/test')
#setcookie(name, value, expires="", domain=None, secure=False): 


class index:
    def GET(self):
        """ Show page """
        posts = model.get_posts()
        c = web.cookies(user_id='')
        if c.user_id != '':    #retrieves cookie user_id
            return render.welcome(posts, c.user_id)
        else:            
            return render.index(posts)


class View:
    def GET(self, id):
        """ View single post """
        post = model.get_post(int(id))
        return render.view(post)


class signup:
    def GET(self):
        return render.signup(user_error="", pwd_error="", email_error="")

    def POST(self):
        i = web.input()
        print i
        
        if i.username and i.pwd and i.email:        #check for fields
            users = db.select('users')  #retrieves "users" table from DB
            ######check if user already exist
            for n in users:
                if n.user_id == i.username:
                    return render.signup(user_error="That user already exist", pwd_error="", email_error="")
                if n.email == i.email:
                    return render.signup(user_error="", pwd_error="", email_error="That email already exist")
            ######
            if i.pwd == i.verypwd:
                web.setcookie('user_id', i.username, 3600)  #set cookie user_id
                db.insert('users', user_id=i.username, pwd=hashlib.sha256(i.pwd+str(3333)).hexdigest(), email=i.email)
                raise web.seeother('/welcome')
            else:
                return render.signup(user_error="", pwd_error="Your passwords didn't match", email_error="")
            
        else:
            #info missing on the forms
            return render.signup(user_error="", pwd_error="", email_error="") 


class welcome:
    def GET(self):
        ####check if user_id cookie has not been manually changed
        c = web.cookies(user_id='')     #retrieves cookie user_id
        users = db.select('users')  #retrieves users table
        for n in users:
            if n.user_id == c.user_id:  #checks if user_id in cookie exist in DB
                posts = model.get_posts()
                return render.welcome(posts, c.user_id)
        #else goto signup page
        raise web.seeother('/login')


class New:
    form = web.form.Form(
        web.form.Textbox('title', web.form.notnull, 
            size=30,
            description="Post title:"),
        web.form.Textarea('content', web.form.notnull, 
            rows=30, cols=80,
            description="Post content:"),
        web.form.Button('Post entry'),
    )

    def GET(self):
        ####check if user_id cookie has not been manually changed
        c = web.cookies(user_id='')     #retrieves cookie user_id
        users = db.select('users')  #retrieves users table
        for n in users:
            if n.user_id == c.user_id:  #checks if user_id in cookie exist in DB
                form = self.form()
                return render.new(form)
        else:
            raise web.seeother('/login')


    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        model.new_post(form.d.title, form.d.content)
        raise web.seeother('/welcome')


class Edit:
    def GET(self, id):
        ####check if user_id cookie has not been manually changed
        c = web.cookies(user_id='')     #retrieves cookie user_id
        users = db.select('users')  #retrieves users table
        for n in users:
            if n.user_id == c.user_id:  #checks if user_id in cookie exist in DB
                post = model.get_post(int(id))
                form = New.form()
                form.fill(post)
                return render.edit(post, form)
        else:
            raise web.seeother('/login')

    def POST(self, id):
        form = New.form()
        post = model.get_post(int(id))
        if not form.validates():
            return render.edit(post, form)
        model.update_post(int(id), form.d.title, form.d.content)
        raise web.seeother('/welcome')


class Delete:
    def POST(self, id):
        ####check if user_id cookie has not been manually changed
        c = web.cookies(user_id='')     #retrieves cookie user_id
        users = db.select('users')  #retrieves users table
        for n in users:
            if n.user_id == c.user_id:  #checks if user_id in cookie exist in DB
                model.del_post(int(id))
                raise web.seeother('/welcome')
        else:
            raise web.seeother('/login')


class login:
    def GET(self):
        return render.login(error="")

    def POST(self):
        i = web.input()
        if i.email and i.pwd:        #check for fields
            pwd = hashlib.sha256(i.pwd+str(3333)).hexdigest()
            ######check if user/pwd are correct
            users = db.select('users')  #retrieves "users" table from DB
            for n in users:
                #print n.user_id, i.username
                #print n.pwd, pwd
                if (n.email == i.email) and (n.pwd == pwd):
                    web.setcookie('user_id', n.user_id, 3600)  #set cookie user_id
                    raise web.seeother('/welcome')
            return render.login(error="Invalid login")    
        else:
            return render.login(error="Invalid login")


class logout:
    def GET(self):
        ####check if user_id cookie has not been manually changed
        web.setcookie('user_id', '', expires=-1)  #set cookie user_id to "empty"
        raise web.seeother('/login')
            

if __name__=="__main__":
    app = web.application(urls, globals())
    app.run()
        
