from django.contrib import admin
from account.models import User,Address,City,Region,AccountDetails
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from fcm_django.models import FCMDevice
# class FCMDeviceAdmin(admin.ModelAdmin):
#     list_display = ('name', 'user', 'device_id', 'active', 'type')

class UserModelAdmin(BaseUserAdmin):
  # The fields to be used in displaying the User model.
  # These override the definitions on the base UserModelAdmin
  # that reference specific fields on auth.User.
  list_display = ('id','email','role', 'tc', 'is_admin')
  list_filter = ('is_admin',)
  fieldsets = (
      ('User Credentials', {'fields': ('email', 'password')}),
      ('Personal info', {'fields': ('name', 'role','tc')}),
      ('Permissions', {'fields': ('is_admin',)}),
  )
  # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
  # overrides get_fieldsets to use this attribute when creating a user.
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('email', 'name', 'role','tc', 'password1', 'password2'),
      }),
  )
  search_fields = ('email',)
  ordering = ('email','id')
  filter_horizontal = ()


class AddressModelAdmin(admin.ModelAdmin):
    list_display = ('region','city','house', 'landmark')

# Now register the new UserModelAdmin...
# admin.site.register( FCMDevice,FCMDeviceAdmin)
admin.site.register(User, UserModelAdmin)
admin.site.register(Address,AddressModelAdmin)
admin.site.register(City)
admin.site.register(Region)
admin.site.register(AccountDetails)