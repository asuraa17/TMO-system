# TMO SYSTEM

## Project Overview
This Django application implements a custom user authentication system with role-based access control for a vehicle management system. The system supports five distinct user roles, each with specific permissions and access levels.

**Project Name:** tmo_system  
**Django App:** users  

## System Roles

The system includes five user roles:

1. **Showroom User** - Vehicle showroom representatives
2. **Buyer** - Customers purchasing vehicles
3. **TMO Officer** - Transport Management Office officers
4. **Field Inspector** - Vehicle inspection officers
5. **System Administrator** - Full system access


## Technical
### 1. Custom User Model

The system uses a custom user model that extends Django's `AbstractUser`:

**Location:** `users/models.py`

**Features:**
- Extends all standard Django User functionality
- Adds a `role` field using `TextChoices`
- Default role: Showroom User
- Maintains compatibility with Django's authentication system

### 2. Role Structure

Roles are defined using Django's `TextChoices`:
- **Database value:** lowercase with underscores (e.g., `tmo_officer`)
- **Display name:** Human-readable format (e.g., "TMO Officer")
- **Default:** All new users are assigned "Showroom User" role

### 3. Automatic Group Assignment

**How it works:**

Groups are automatically created and assigned using Django signals:

**Location:** 
- `users/signals.py` - Handles new user creation
- `users/admin.py` - Handles role updates via admin panel using `save_related` method


**Process:**

**For New Users:**
1. When a user is created, a `post_save` signal fires
2. The signal checks the user's role
3. Creates the corresponding group if it doesn't exist
4. Adds the user to the correct group

**For Role Changes (via Admin):**
1. When a user's role is changed in the admin panel
2. The `save_related` method in `UserAdmin` automatically updates groups
3. Clears any existing group assignments
4. Adds the user to the new group matching their role

**Group Mapping:**
- Showroom User → `showroom_user` group
- Buyer → `buyer` group
- TMO Officer → `tmo_officer` group
- Field Inspector → `inspector` group
- System Administrator → `system_admin` group

### 4. Creating Users via Django Admin

1. **Login to Admin Panel**
   - Navigate to `http://localhost:8000/admin/`
   - Enter superuser credentials

2. **Add New User**
   - Click "Users" under USERS section
   - Click "Add User" button
   - Enter username and password
   - Click "Save and continue editing"

3. **Set User Role**
   - Scroll to "Role Information" section
   - Select appropriate role from dropdown
   - Click "Save"

4. **Verify Group Assignment**
   - User is automatically added to corresponding group
   - No manual group assignment needed


### 5. Testing Role-Based Access

#### Test 1: General Dashboard Access

1. Create users with different roles
2. Login to admin panel
3. Visit `http://localhost:8000/users/dashboard/`
4. **Result:** All authenticated users can access

#### Test 2: TMO Dashboard Access

**As TMO Officer:**
1. Login as user with "TMO Officer" role
2. Visit `http://localhost:8000/users/tmo/`
3. **Result:** Access granted, page displays

**As Other Role:**
1. Login as user with any other role
2. Visit `http://localhost:8000/users/tmo/`
3. **Result:** Redirected to `/users/dashboard/`

#### Test 3: Role Change Updates Group

1. Login to admin
2. Open an existing user
3. Change their role (e.g., Showroom User → Buyer)
4. Save
5. **Result:** User removed from old group, added to new group