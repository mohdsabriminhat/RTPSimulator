from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('homepage/', views.homepage, name='homepage'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_homepage/', views.admin_homepage, name='admin_homepage'),
    path('approve_visitor/<int:id>/', views.approve_visitor, name='approve_visitor'),
    path('delete_visitor/<int:id>/', views.delete_visitor, name='delete_visitor'),
    path('visitor_management/', views.visitor_management, name='visitor_management'),  
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('instructor_management/', views.instructor_management, name='instructor_management'),
    path('approve_instructor/<int:id>/', views.approve_instructor, name='approve_instructor'),
    path('delete_instructor/<int:instructor_id>/', views.delete_instructor, name='delete_instructor'),
    #path('test/', views.test, name='test'),
    path('profile/', views.profile, name='profile'),
    path('instructor/profile/', views.instructor_profile, name='instructor_profile'),
    path('instructor/homepage/', views.instructor_homepage, name='instructor_homepage'),
    path('request-cert/', views.request_cert, name='certificate_request_form'),
    path('certificate-request-success/', views.certificate_request_success, name='certificate_request_success'),
    path('mainpage/', views.mainpage, name='mainpage'),
    path('certificate_request_list/', views.certificate_requests_list, name='certificate_request_list'),
    path('certificate-requests/approve/<int:id>/', views.approve_certificate_request, name='approve_certificate_request'),
    path('certificate-requests/reject/<int:id>/', views.reject_certificate_request, name='reject_certificate_request'),
    path('certificate-requests/delete/<int:id>/', views.delete_certificate_request, name='delete_certificate_request'),
    path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('generate-certificate/', views.generate_certificate, name='generate_certificate'),
    path('visitor2/', views.visitor2, name='visitor2'),
    
    
]



