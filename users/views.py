from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .form import RegisterForm,modifierForm
from .models import cop,reponse,registeruser
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from Multiple import settings
from django.http import Http404
from .models import User as CustomUser

User=get_user_model()
# Create your views here.



def RegisterUser(request):
    if request.method=="POST":
        grade=request.POST['grade']
        prenom=request.POST['prenom']
        nom=request.POST['nom']
        email=request.POST['email']
        matricule=request.POST['matricule']
        image=request.FILES['image']
        promotion=request.POST['promotion']
        commandant_promotion=request.POST['commandant_promotion']
        password=request.POST['password']
        password1=request.POST['password1']

        if registeruser.objects.filter(matricule=matricule):
            messages.error(request,"votre matricule est déjà utiliser")
            return redirect('RegisterUser')
        
        
        if not matricule.isalnum():
            messages.error(request,"le matricule doit étre une alphanumérique")
            return redirect('RegisterUser')
        
        if registeruser.objects.filter(email=email):
            messages.error(request,"votre email est déjà utiliser")
            return redirect('RegisterUser')
        
        if password!=password1:
            messages.error(request,"votre password ne coincide pas")
            return redirect('RegisterUser')

        saveUser=registeruser.objects.create(
            grade=grade,
            prenom=prenom,
            nom=nom,
            email=email,
            matricule=matricule,
            image=image,
            promotion=promotion,
            commandant_promotion=commandant_promotion,
            password=password,
            password1=password1,
        )

        if saveUser:
            messages.success(request,"Votre compte est vien créer")

            subject="Bienvenue sur ISP App Permission"
            message="Nous sommes comptants de vous voire sur notre App"
            from_email=settings.EMAIL_HOST_USER
            to_list=[saveUser.email]
            send_mail(subject,message,from_email,to_list)
            return redirect('connexionUser')
        
        else:
            return redirect('RegisterUser')
    return render(request,'RegisterUser.html')

def dir_get_perm(request,id):
    get_Register_all=get_object_or_404(cop,id=id)
    
    if request.method=="POST":
        accords=request.POST['accords']
        date_aller=request.POST['date_aller']
        date_retour=request.POST['date_retour']
        # Signe=request.POST.get('Signe',False)

        saveReponse=reponse.objects.create(
            Cop=get_Register_all,
            accords=accords,
            date_aller=date_aller,
            date_retour=date_retour,
            )

        if saveReponse:
            return redirect('directeur')
    return render(request,'dir_get_perm.html',{'get_Register_all':get_Register_all})

def directeur(request):
    #all_permission=cop.objects.all()
    all_permission=cop.objects.all()

    if request.method == "POST":
        query = request.POST['q']

        if query != "":
            searched_objects=cop.objects.filter(demandeur=query).all()
        else: 
            searched_objects=cop.objects.all()

        return render(request,"directeur.html",{'all_permission':searched_objects})
    return render(request,"directeur.html",{'all_permission':all_permission})


def commandant(request):
    return render(request,"commandant.html")

def secraiteur(request):
    all_permission=cop.objects.all()
    if request.method == "POST":
        query = request.POST['q']

        if query != "":
            searched_objects=cop.objects.filter(demandeur=query).all()

            if not searched_objects.exists():
                results_found = False

        else: 
            searched_objects=cop.objects.all()

        return render(request,'secraiteur.html',{'all_permission':searched_objects,'results_found':results_found})
    return render(request,'secraiteur.html',{'all_permission':all_permission})

def compte(request):
    all_permission=cop.objects.all()
    if request.method == "POST":
        query = request.POST['q']

        if query != "":
            searched_objects=cop.objects.filter(demandeur=query).all()
        else: 
            searched_objects=cop.objects.all()

        return render(request,'registers.html',{'all_permission':searched_objects})
    return render(request,'registers.html',{'all_permission':all_permission})

def connexionUser(request):
    if request.method=="POST":
        matricule=request.POST['username']
        password=request.POST['password']

        user=registeruser.objects.get(matricule=matricule,password=password)

        if user is not None:
            request.session['matricule']=user.matricule
            return redirect('cop')
        else:
            return redirect('connexionUser')
    return render(request,'loginUser.html')

def cops(request):
    matricule = request.session.get('matricule')
    
    if matricule is not None :
        
        try:
            name=registeruser.objects.filter(matricule=matricule).all()
            if request.method=="POST":
                motif=request.POST['motif']
                date_aller=request.POST['date_aller']
                date_retour=request.POST['date_retour']

                demandeur=registeruser.objects.get(matricule=matricule)

                savePermission=cop.objects.create(
                    demandeur=demandeur,
                    motif=motif,
                    date_aller=date_aller,
                    date_retour=date_retour
                )

                if savePermission:
                    savePermission.save()
                    return HttpResponse("Envoyer avec succes")
            return render(request,"cop.html", { 'matricule': matricule,'name':name })
        except registeruser.DoesNotExist:
            return HttpResponse("Vous n'Etes pas enregister")
    return render(request,"cop.html")
    
def cop_vue_reponse(request, matricule):
    # obj=cop.objects.all()
    matricule = request.session.get('matricule')
    all_permission=cop.objects.filter(demandeur = matricule).all()
    return render(request,"cop_vue_reponse.html",{'all_permission':all_permission})

def reponse_dir(request, id):
    all_permission=get_object_or_404(cop,id=id)
    get_reponse=all_permission.reponse_set.all()
    return render(request,"reponse_dir.html",{'all_permission':all_permission,'get_reponse':get_reponse})


def sous_off(request):
    return render(request,"sous_off.html")

def connexion(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            print("vous etes connecter")
            if user.is_directeur:
                return redirect('directeur')
            
            elif user.is_secraiteur:
                return redirect('secraiteur')
            
            else:
                return redirect('sous_off')
        else:
            messages.error(request,"Mauvaise authentification")
            return redirect('login')
        
    return render(request,'login.html')

def deconnexion(request):
    logout(request)
    request.session.delete()
    return redirect('login')

def deconnexionUser(request):
    logout(request)
    request.session.delete()
    return redirect('connexionUser')

def register(request):
    form=RegisterForm()
    if request.method=="POST":
        form=RegisterForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    return render(request, 'register.html', {'form': form})




def get_permission(request):

    print(request.build_absolute_uri())
    all_permission=cop.objects.all()
    if request.method == "POST":
        query = request.POST['q']
        print(query)

        if query != "":
            searched_objects=cop.objects.filter(demandeur=query).all()
        else: 
            searched_objects=cop.objects.all()
            
        return render(request,"all_permission.html",{'all_permission':searched_objects})
    return render(request,'all_permission.html',{'all_permission':all_permission})

def Reponse(request,matricule):
    get_Register_all=get_object_or_404(registeruser,matricule=matricule)
    permission_send=get_Register_all.cop_set.all()
    
    if request.method=="POST":
        accords=request.POST['accords']
        # Signe=request.POST.get('Signe',False)

        Cop=cop.objects.get(matricule=matricule)
        saveReponse=reponse.objects.create(Cop=Cop,
            accords=accords,
            # Signe=bool(Signe),
        )

        if saveReponse:
            saveReponse.save()
            return redirect('directeur')
    return render(request,'dir_get_perm.html',{'get_Register_all':get_Register_all,'permission_send':permission_send})


def all_reponse(request,id):
    cop_obj = get_object_or_404(cop, id=id)
    # cop_obj_reg=cop_obj.demandeur
    # reponse_id=get_object_or_404(reponse,id=id)
    # reponse_sender=reponse_id.Cop
    reponses=cop_obj.reponse_set.all()
    if request.method == "POST":
        # Logique pour traiter les données du formulaire en cas de requête POST
        # Assurez-vous de remplacer cette logique avec votre propre code

        return HttpResponse("Traitement des données POST")

    # Si la requête est GET, afficher simplement les informations sur l'objet "cop" et ses réponses
    return render(request, 'all_reponse.html', {'cop_obj': cop_obj,'reponses':reponses})

def update(request,id):
    obj=get_object_or_404(cop,id=id)
    
    form=modifierForm(instance=obj)
    if request.method=="POST":
        form=modifierForm(data=request.POST,instance=obj)
        if form.is_valid():
            form.save()
            return redirect('cop')
        # else:
        #     return render(request,'modifier.html',{'form':form})
    return render(request,'modifier.html',{'form':form,'obj':obj})

def deletePerm(request,id):
    try:
        obj=cop.objects.get(id=id)
        name=obj.demandeur.nom
    except cop.DoesNotExist:
        raise Http404("Page not Found")
    if request.method=="POST":
        obj.delete()
        return redirect('cop')
    return render(request,'delete.html',{'obj':obj,'name':name})

def demande_permission(request,id):
    get_obj_demandeur=get_object_or_404(cop,id=id)
    obj_demandeur=get_obj_demandeur.demandeur
    return render()

def ResetPWDPage(request, matricule):

    user = registeruser.objects.get(matricule=matricule)
    
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            user.password = password
            user.password1 = confirm_password
            user.save()
            return HttpResponse('<h1>Votre mot de passe a été réinitialisé avec succès</h1>')
        else:
            print('Passwords do not match')
            return HttpResponse('<h1>Les mots de passe sont différents.<br>Veuillez réessayer</h1>')

    return render(request, 'ResetPWDPage.html', {'matricule':matricule})

def resetPwd(request):
    if request.method == 'POST':
        email = request.POST['email']
        matricule = request.POST['matricule']
        
        try:
            isMatching = registeruser.objects.get(matricule=matricule, email=email)
            
            print("User does exist")

            subject = "Reset password appeal accepted"
            # reset_link = request.build_absolute_uri(reverse('resetPWD_page'))  # Generate reset password URL
            reset_link = request.build_absolute_uri(f'/reset-password/{matricule}')  # Generate reset password URL
            #print(reset_link)

            message = render_to_string('SendMail.html', {
                'reset_link': reset_link, 'email': email, 'matricule': matricule
            })
            
            from_mail = settings.EMAIL_HOST_USER
            to_mails = [email]
            isMailSent = EmailMessage(subject, message, from_mail, to_mails)
            isMailSent.content_subtype = 'html'

            if isMailSent.send():
                msg_success = f'Vous avez reçu un email sur cette adresse {email}'
                print(msg_success)
                return render(request, "resetPWD_Success.html", {'msg_success': msg_success})

        except Exception as e:
            print("User does not exist:", str(e))

    return render(request, 'reset_password.html', {})


def add_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        is_directeur = 'is_directeur' in request.POST
        is_commandant = 'is_commandant' in request.POST
        is_secraiteur = 'is_secretaire' in request.POST

        if CustomUser.objects.filter(username=username).exists():
            # Gérer le cas où l'utilisateur existe déjà
            # Vous pouvez afficher un message d'erreur ou rediriger l'utilisateur vers une autre page
            # Par exemple :
            return HttpResponse('Cet utilisateur existe déjà.')


        user = get_user_model().objects.create_user(username=username, password=password)
        custom_user = CustomUser.objects.create(user=user)  # Créez un objet CustomUser associé à l'utilisateur

        # Attribuez les rôles en fonction des valeurs booléennes
        custom_user.is_directeur = is_directeur
        custom_user.is_commandant = is_commandant
        custom_user.is_secraiteur = is_secraiteur
        
        custom_user.save()
        print("utilisateur ajouter:",custom_user)

        return HttpResponse("Ajouter Avec Succes")  # Rediriger vers la page des utilisateurs après l'ajout

    return render(request, 'add_user.html')