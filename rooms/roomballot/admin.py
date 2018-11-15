from django.contrib import admin

from .models import *

admin.site.register(Room)
admin.site.register(Staircase)
admin.site.register(Image)
admin.site.register(Student)
admin.site.register(Syndicate)
admin.site.register(AdminUser)
admin.site.register(Review)
admin.site.register(Setting)
admin.site.register(Floorplan)
admin.site.register(Band)

admin.site.site_header = "Downing JCR RBS"
admin.site.site_title = "Downing JCR RBS"
admin.site.index_title = "Backend Administration"