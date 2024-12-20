from account.data import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from account.models import User, Address, Category
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage
from django.template.loader import render_to_string
from datetime import datetime
import re

@login_required
def account_edit(request):
    try:
        # Obtém o endereço associado ao usuário
        if request.method == "POST":
            
            data = request.POST
            user = request.user
            
            phone_number = data.get('phone_number', user.phone_number)
            postal_code = data.get('postal_code', user.phone_number)
            bio = data.get('bio', user.bio)
            categories = data.getlist('categories[]')
            
            # Validação do Telefone
            if phone_number:
                phone = re.sub(r'\D', '', phone_number)  # Remove tudo que não for número
                if len(phone) > 13 or not phone.startswith('55'):
                    return JsonResponse({"success": False, "message": "Número de telefone inválido. Deve ser no formato 5521912345678."}, status=400)
                    
            # Validação do CEP
            if postal_code:
                code = re.sub(r'\D', '', postal_code)  # Remove tudo que não for número
                if len(code) == 8:
                    formatted_cep = f"{code[:5]}-{code[5:]}"
                    postal_code = formatted_cep
                else:
                    return JsonResponse({"success": False, "message": "CEP inválido. Deve ser no formato 12345-678."}, status=400)
                    
            # Validação da biografia
            if bio and len(bio) > 500:
                return JsonResponse({"success": False, "message": "A biografia não pode ter mais de 500 caracteres."}, status=400)
                    

            # Atualiza os dados do usuário (exemplo simplificado)
            user.phone_number = phone_number 
            user.bio = bio
            
            if categories:
                selected_categories = Category.objects.filter(id__in=categories)
                user.categories.set(selected_categories)  # Atualiza as categorias associadas
            
            # Atualiza a foto de perfil, se fornecida
            if "profile_picture" in request.FILES:
                user.profile_image = request.FILES["profile_picture"]
            
            user.save()

            # Atualiza o endereço (exemplo)
            address = user.address
            address.city = data.get('city', address.city)
            address.state = data.get('state', address.state)
            address.postal_code = postal_code
            address.address_line = data.get('address_line', address.address_line)
            address.address_number = data.get('address_number', address.address_number)
            address.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return JsonResponse({"success": True}, status=201)
        
        messages.error(request, "Method invalido!")
        return redirect("index")
    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "message": "Algo deu errado, tente outra vez mais tarde!"}, status=405)
    

def account_block(request):
    return

def account_delete(request):
    return


@login_required
def follow_user(request, user_id):
    try:
        if request.method == 'POST':
            user_to_follow = get_object_or_404(User, id=user_id)

            # Assuming you have a `following` ManyToManyField in your User model
            request.user.following.add(user_to_follow)

            return JsonResponse({"success": True})
        return JsonResponse({"error": "Invalid request"}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "message": "Algo deu errado, tente outra vez mais tarde!"}, status=405)


@login_required
def get_profile(request, user_id):
    try:
        """
        View to fetch and return user profile data in JSON format.
        """
        user = get_object_or_404(User, id=user_id)

        profile_data = {
            "name": user.username,
            "profile_image": user.profile_image.url if user.profile_image else "/static/images/default-profile.png",
            "bio": user.bio or "Bio não informada",
            "address": str(user.address) if hasattr(user, 'address') else "Endereço não informado",
            "typeuser": user.get_typeuser_display(),  # Retorna a descrição do tipo de usuário
            "categories": [{"id": category.id, "name": category.name} for category in user.categories.all()],  # Lista de categorias
            "followers_count": user.followers.count() if hasattr(user, 'followers') else 0,  # Contagem de seguidores
            "is_following": request.user.following.filter(id=user.id).exists() if hasattr(request.user, 'following') else False
        }

        return JsonResponse({"success": True, 'profile': profile_data}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "message": "Algo deu errado, tente outra vez mais tarde!"}, status=405)



@login_required
def get_followers(request):
    try:
        user = request.user
        followers = user.followers.all()  # Obtem os seguidores do usuário
        if len(followers) < 0:
           return JsonResponse({"success": True , 'html': "<p> Você não tem nenhum Seguidor </p>"})
        html = render_to_string("partials/followers_list.html", {"followers": followers})
        print(html)
        return JsonResponse({"success": True , 'html': html})
    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "message": "Algo deu errado, tente outra vez mais tarde!"}, status=405)
    
@login_required
def get_organizations(request, page):
    try:
        # Filtrar usuários do tipo organização com ordenação
        organizations = User.objects.filter(typeuser="organization").order_by("id")

        # Configurar o paginator
        paginator = Paginator(organizations, 20)

        try:
            organizations_page = paginator.page(page)
        except EmptyPage:
            return JsonResponse({"html": "", "success": False, "has_more": False}, status=200)

        for org in organizations_page:
             org.joined = org.date_joined.strftime("%d de %B de %Y").capitalize()
             
        # Renderizar o HTML
        html = render_to_string("partials/org_list.html", {"organizations": organizations_page})

        return JsonResponse(
            {"success": True, "html": html, "has_more": organizations_page.has_next()}, 
            status=200
        )

    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "message": "Algo deu errado, tente outra vez mais"})