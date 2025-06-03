class DepartmentType(AbsoluteBaseModel):
    name = models.CharField(max_length=100)  
    is_academic = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Department(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    department_type = models.ForeignKey(DepartmentType, on_delete=models.CASCADE)
    

    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    office = models.CharField(max_length=255, null=True, blank=True)
    
    def clean(self):
  
        if self.department_type.is_academic and not self.school:
            raise ValidationError("Academic departments must be assigned to a school")
    
    def __str__(self):
        return self.name
    
class SubDepartment(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    parent_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='sub_departments')
    office = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.parent_department.name} - {self.name}"
    
    @property
    def department_type(self):
        return self.parent_department.department_type
    
    @property  
    def school(self):
        return self.parent_department.school
    
    
class Staff(AbsoluteBaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    staff_number = models.CharField(max_length=255) 
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    sub_department = models.ForeignKey(SubDepartment, on_delete=models.CASCADE, null=True, blank=True)
    position = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_main_department(self):
        if self.sub_department:
            return self.sub_department.parent_department
        return self.department