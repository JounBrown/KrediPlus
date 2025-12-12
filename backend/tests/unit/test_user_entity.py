"""
Unit tests for User entity
"""
import pytest
from datetime import datetime
from src.domain.entities.user import User


class TestUserEntity:
    """Test User entity functionality"""
    
    def test_user_creation_with_required_fields(self):
        """Test creating a user with required fields only"""
        # Arrange & Act
        user = User(
            id="user123",
            email="test@example.com"
        )
        
        # Assert
        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.role is None
        assert user.created_at is None
        assert user.last_sign_in_at is None
    
    def test_user_creation_with_all_fields(self):
        """Test creating a user with all fields"""
        # Arrange
        created_at = datetime(2024, 1, 15, 10, 30, 0)
        last_sign_in = datetime(2024, 6, 20, 14, 45, 30)
        
        # Act
        user = User(
            id="admin456",
            email="admin@company.com",
            role="admin",
            created_at=created_at,
            last_sign_in_at=last_sign_in
        )
        
        # Assert
        assert user.id == "admin456"
        assert user.email == "admin@company.com"
        assert user.role == "admin"
        assert user.created_at == created_at
        assert user.last_sign_in_at == last_sign_in
    
    def test_user_creation_with_partial_fields(self):
        """Test creating a user with some optional fields"""
        # Arrange
        created_at = datetime(2024, 3, 10, 9, 15, 0)
        
        # Act
        user = User(
            id="user789",
            email="user@domain.com",
            role="user",
            created_at=created_at
        )
        
        # Assert
        assert user.id == "user789"
        assert user.email == "user@domain.com"
        assert user.role == "user"
        assert user.created_at == created_at
        assert user.last_sign_in_at is None


class TestUserRoleValidation:
    """Test user role validation methods"""
    
    def test_is_admin_true(self):
        """Test is_admin returns True for admin users"""
        # Arrange
        admin_user = User(
            id="admin001",
            email="admin@company.com",
            role="admin"
        )
        
        # Act & Assert
        assert admin_user.is_admin() == True
    
    def test_is_admin_false_for_non_admin_roles(self):
        """Test is_admin returns False for non-admin roles"""
        non_admin_roles = ["user", "moderator", "guest", "viewer", "editor", "manager"]
        
        for role in non_admin_roles:
            user = User(
                id=f"user_{role}",
                email=f"{role}@company.com",
                role=role
            )
            assert user.is_admin() == False, f"Role '{role}' should not be admin"
    
    def test_is_admin_false_for_none_role(self):
        """Test is_admin returns False when role is None"""
        # Arrange
        user = User(
            id="user_no_role",
            email="norole@company.com",
            role=None
        )
        
        # Act & Assert
        assert user.is_admin() == False
    
    def test_is_admin_false_for_empty_role(self):
        """Test is_admin returns False for empty string role"""
        # Arrange
        user = User(
            id="user_empty_role",
            email="empty@company.com",
            role=""
        )
        
        # Act & Assert
        assert user.is_admin() == False
    
    def test_is_admin_case_sensitive(self):
        """Test is_admin is case sensitive"""
        case_variations = ["Admin", "ADMIN", "AdMiN", "admin "]
        
        for role_variation in case_variations:
            user = User(
                id=f"user_{role_variation}",
                email=f"{role_variation}@company.com",
                role=role_variation
            )
            assert user.is_admin() == False, f"Role '{role_variation}' should not be admin (case sensitive)"


class TestUserActiveStatus:
    """Test user active status validation"""
    
    def test_is_active_true_for_valid_users(self):
        """Test is_active returns True for users with id and email"""
        # Test with minimal required fields
        user1 = User(
            id="active_user1",
            email="active1@company.com"
        )
        assert user1.is_active() == True
        
        # Test with all fields
        user2 = User(
            id="active_user2",
            email="active2@company.com",
            role="user",
            created_at=datetime.now(),
            last_sign_in_at=datetime.now()
        )
        assert user2.is_active() == True
        
        # Test with admin role
        user3 = User(
            id="admin_user",
            email="admin@company.com",
            role="admin"
        )
        assert user3.is_active() == True
    
    def test_is_active_false_for_missing_id(self):
        """Test is_active returns False when id is None"""
        # Arrange
        user = User(
            id=None,
            email="noid@company.com",
            role="user"
        )
        
        # Act & Assert
        assert user.is_active() == False
    
    def test_is_active_false_for_missing_email(self):
        """Test is_active returns False when email is None"""
        # Arrange
        user = User(
            id="user_no_email",
            email=None,
            role="user"
        )
        
        # Act & Assert
        assert user.is_active() == False
    
    def test_is_active_false_for_missing_both(self):
        """Test is_active returns False when both id and email are None"""
        # Arrange
        user = User(
            id=None,
            email=None,
            role="user"
        )
        
        # Act & Assert
        assert user.is_active() == False
    
    def test_is_active_with_empty_strings(self):
        """Test is_active behavior with empty strings"""
        # Note: Current implementation only checks for None, not empty strings
        # Test empty id (still considered active since it's not None)
        user1 = User(
            id="",
            email="test@company.com"
        )
        assert user1.is_active() == True  # Empty string is not None
        
        # Test empty email (still considered active since it's not None)
        user2 = User(
            id="user123",
            email=""
        )
        assert user2.is_active() == True  # Empty string is not None
        
        # Test both empty (still considered active since neither is None)
        user3 = User(
            id="",
            email=""
        )
        assert user3.is_active() == True  # Empty strings are not None


class TestUserBusinessLogic:
    """Test user business logic and patterns"""
    
    def test_admin_user_workflow(self):
        """Test complete admin user workflow"""
        # Arrange
        admin = User(
            id="admin_workflow",
            email="admin@company.com",
            role="admin",
            created_at=datetime(2024, 1, 1, 10, 0, 0)
        )
        
        # Act & Assert
        assert admin.is_active() == True
        assert admin.is_admin() == True
        assert admin.role == "admin"
        assert admin.created_at is not None
    
    def test_regular_user_workflow(self):
        """Test complete regular user workflow"""
        # Arrange
        user = User(
            id="regular_user",
            email="user@company.com",
            role="user",
            created_at=datetime(2024, 2, 15, 14, 30, 0),
            last_sign_in_at=datetime(2024, 6, 20, 9, 45, 0)
        )
        
        # Act & Assert
        assert user.is_active() == True
        assert user.is_admin() == False
        assert user.role == "user"
        assert user.last_sign_in_at is not None
    
    def test_user_without_role_workflow(self):
        """Test user without specific role"""
        # Arrange
        user = User(
            id="no_role_user",
            email="norole@company.com"
        )
        
        # Act & Assert
        assert user.is_active() == True
        assert user.is_admin() == False
        assert user.role is None
    
    def test_user_role_assignment_patterns(self):
        """Test different role assignment patterns"""
        roles = ["admin", "user", "moderator", "guest", "viewer", "editor", "manager", "supervisor"]
        
        for role in roles:
            user = User(
                id=f"user_{role}",
                email=f"{role}@company.com",
                role=role
            )
            
            assert user.is_active() == True
            assert user.role == role
            
            # Only "admin" role should return True for is_admin()
            if role == "admin":
                assert user.is_admin() == True
            else:
                assert user.is_admin() == False


class TestUserEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_user_with_special_characters_in_email(self):
        """Test user with special characters in email"""
        special_emails = [
            "user+tag@company.com",
            "user.name@company.com",
            "user_name@company.com",
            "user-name@company.com",
            "123user@company.com",
            "user123@company.com",
            "user@sub.company.com",
            "user@company-name.com"
        ]
        
        for email in special_emails:
            user = User(
                id=f"user_{hash(email)}",
                email=email,
                role="user"
            )
            assert user.is_active() == True, f"Email '{email}' should be valid"
            assert user.email == email
    
    def test_user_with_special_characters_in_id(self):
        """Test user with special characters in id"""
        special_ids = [
            "user-123",
            "user_456",
            "user.789",
            "user@domain",
            "123-456-789",
            "uuid-like-id-123",
            "user+special"
        ]
        
        for user_id in special_ids:
            user = User(
                id=user_id,
                email="test@company.com",
                role="user"
            )
            assert user.is_active() == True, f"ID '{user_id}' should be valid"
            assert user.id == user_id
    
    def test_user_with_very_long_fields(self):
        """Test user with very long field values"""
        # Test long ID
        long_id = "a" * 200
        user1 = User(
            id=long_id,
            email="test@company.com"
        )
        assert user1.is_active() == True
        assert user1.id == long_id
        
        # Test long email
        long_email = "a" * 100 + "@company.com"
        user2 = User(
            id="user123",
            email=long_email
        )
        assert user2.is_active() == True
        assert user2.email == long_email
        
        # Test long role
        long_role = "a" * 100
        user3 = User(
            id="user456",
            email="test@company.com",
            role=long_role
        )
        assert user3.is_active() == True
        assert user3.is_admin() == False  # Not "admin"
        assert user3.role == long_role
    
    def test_user_with_whitespace_in_fields(self):
        """Test user with whitespace in fields"""
        # Test ID with whitespace
        user1 = User(
            id="  user123  ",
            email="test@company.com"
        )
        assert user1.is_active() == True  # Whitespace doesn't affect truthiness
        assert user1.id == "  user123  "
        
        # Test email with whitespace
        user2 = User(
            id="user456",
            email="  test@company.com  "
        )
        assert user2.is_active() == True
        assert user2.email == "  test@company.com  "
        
        # Test role with whitespace
        user3 = User(
            id="user789",
            email="test@company.com",
            role="  admin  "
        )
        assert user3.is_active() == True
        assert user3.is_admin() == False  # Not exactly "admin"
        assert user3.role == "  admin  "
    
    def test_user_datetime_edge_cases(self):
        """Test user with various datetime values"""
        # Test very old date
        old_date = datetime(1970, 1, 1, 0, 0, 0)
        user1 = User(
            id="old_user",
            email="old@company.com",
            created_at=old_date,
            last_sign_in_at=old_date
        )
        assert user1.is_active() == True
        assert user1.created_at == old_date
        assert user1.last_sign_in_at == old_date
        
        # Test future date
        future_date = datetime(2030, 12, 31, 23, 59, 59)
        user2 = User(
            id="future_user",
            email="future@company.com",
            created_at=future_date,
            last_sign_in_at=future_date
        )
        assert user2.is_active() == True
        assert user2.created_at == future_date
        assert user2.last_sign_in_at == future_date
        
        # Test microseconds precision
        precise_date = datetime(2024, 6, 15, 14, 30, 45, 123456)
        user3 = User(
            id="precise_user",
            email="precise@company.com",
            created_at=precise_date,
            last_sign_in_at=precise_date
        )
        assert user3.is_active() == True
        assert user3.created_at == precise_date
        assert user3.last_sign_in_at == precise_date
    
    def test_user_data_immutability_during_validation(self):
        """Test that validation methods don't modify user data"""
        # Arrange
        original_data = {
            'id': "immutable_user",
            'email': "immutable@company.com",
            'role': "admin",
            'created_at': datetime(2024, 1, 1, 12, 0, 0),
            'last_sign_in_at': datetime(2024, 6, 1, 15, 30, 0)
        }
        
        user = User(**original_data)
        
        # Act - Call validation methods multiple times
        for _ in range(5):
            user.is_admin()
            user.is_active()
        
        # Assert - Data should remain unchanged
        assert user.id == original_data['id']
        assert user.email == original_data['email']
        assert user.role == original_data['role']
        assert user.created_at == original_data['created_at']
        assert user.last_sign_in_at == original_data['last_sign_in_at']
    
    def test_user_equality_and_identity(self):
        """Test user object equality and identity"""
        # Create two users with same data
        user1 = User(
            id="same_user",
            email="same@company.com",
            role="user"
        )
        
        user2 = User(
            id="same_user",
            email="same@company.com",
            role="user"
        )
        
        # They should have same data but be different objects
        assert user1.id == user2.id
        assert user1.email == user2.email
        assert user1.role == user2.role
        assert user1 is not user2  # Different objects
    
    def test_user_role_variations_comprehensive(self):
        """Test comprehensive role variations"""
        role_test_cases = [
            ("admin", True),
            ("ADMIN", False),
            ("Admin", False),
            ("admin ", False),
            (" admin", False),
            ("admin\n", False),
            ("admin\t", False),
            ("administrator", False),
            ("admin_user", False),
            ("user_admin", False),
            ("", False),
            (None, False),
            ("user", False),
            ("guest", False),
            ("moderator", False)
        ]
        
        for role, expected_is_admin in role_test_cases:
            user = User(
                id=f"test_{hash(str(role))}",
                email="test@company.com",
                role=role
            )
            
            assert user.is_admin() == expected_is_admin, f"Role '{role}' should return {expected_is_admin} for is_admin()"
            assert user.is_active() == True  # All should be active (have id and email)