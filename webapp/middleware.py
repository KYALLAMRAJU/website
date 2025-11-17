# from django.http import HttpResponse
#
# class ExecutionFlowMiddleware(object):
#
#     def __init__(self,get_response):
#         print("Middleware Initialized")
#         self.get_response=get_response # One-time configuration and initialization.
#
#
#     def __call__(self,request):
#         # Code to be executed for each request before the view (and later middleware) are called.
#         print("Before View Execution:Pre-processing Request using middleware")
#         response=self.get_response(request) # the view is called.Code to be executed for each request/response after
#         print("After View Execution-Post-processing Response using middleware")
#         return response
#
#     def process_exception(self,request,exception):
#         print("Exception Occurred:",exception)
#         # You can return a custom response here if needed
#         return HttpResponse("<h1>Currently we are facing some technical issue. Please try again later.- We will get back as soon as possible.</h1>")
#     #this method is called when an exception occurs during the processing of a request. i.e in view or other middleware.