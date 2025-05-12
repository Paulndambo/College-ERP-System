from django.urls import path

from .views import StudentDocumentCreateView, StudentDocumentHistoryListView, StudentDocumentUpdateView, StudentEducationHistoryCreateView, StudentEducationHistoryListView, StudentEducationHistoryUpdateView, StudentMealCardCreateView, StudentMealCardListView, StudentMealCardUpdateView, StudentProgrameCreateView, StudentProgrameListView, StudentProgrammeUpdateView, StudentRegistrationView, StudentUpdateView



urlpatterns = [
    path("create-student/", StudentRegistrationView.as_view(),  name="create-student" ),
    path("update-student/",StudentUpdateView.as_view(),name="update-student" ),
    
    
    #Eduaction history
    path('education-history/create/', StudentEducationHistoryCreateView.as_view(), name='student-education-create'),
    path('education-history/', StudentEducationHistoryListView.as_view(), name='student-education-history'),
    path('education/update/<int:pk>/', StudentEducationHistoryUpdateView.as_view(), name='student-education-update'),
     
    #Documents
    path('documents/create/', StudentDocumentCreateView.as_view(), name='student-document-create'),
    path('documents/', StudentDocumentHistoryListView.as_view(), name='student-documents'),
    path('documents/update/<int:pk>/', StudentDocumentUpdateView.as_view(), name='student-document-update'),
    
    #Programmes
    path('programme/create/', StudentProgrameCreateView.as_view(), name='student-programme-create'),
    path('programmes/', StudentProgrameListView.as_view(), name='student-programmes'),
    path('programme/update/<int:pk>/', StudentProgrammeUpdateView.as_view(), name='student-programme-update'),
    
    #Meal Cards
    path('mealcards/create/', StudentMealCardCreateView.as_view(), name='student-mealcard-create'),
    path('mealcards/', StudentMealCardListView.as_view(), name='student-mealcards'),
    path('mealcards/update/<int:pk>/', StudentMealCardUpdateView.as_view(), name='student-mealcard-update'),
    
]
