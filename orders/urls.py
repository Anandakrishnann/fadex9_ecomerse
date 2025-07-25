from django.urls import path
from . views import *
from . import views

app_name = 'order'

urlpatterns = [
    path('place_order/', OrderVerificationView.as_view(), name='place_order'),
    path('online_payment/', OnlinePayment.as_view(), name='online_payment'),
    path('individual_cancel/<int:pk>/', IndividualCancel.as_view(), name='individual_cancel'),
    path('individual_return/<int:pk>/', IndividualReturn.as_view(), name='individual_return'),
    path('order_success/', OrderSuccess.as_view(), name='order_success'),
    path('orders',AdminOrder.as_view(), name='admin_orders'),
    path('order_details/<int:pk>/',AdminOrderDetails.as_view(), name='admin_orders_details'),
    path('cancel_order/<int:pk>/',CancelOrders.as_view(), name='cancel_order'),
    path('admin_cancel_order/<int:pk>/',AdminCancelOrders.as_view(), name='admin_cancel_order'),
    path('return_order/<int:pk>/',ReturnOrders.as_view(), name='return_order'),
    path('return_requests/',AdminReturnRequests.as_view(), name='return_requests'),
    path('admin_return_approval/<int:pk>/',AdminReturnApproval.as_view(), name='admin_return_approval'),
]
