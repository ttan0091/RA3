// Example: Complete UserProfile Component using Colocation Pattern
// This shows a realistic implementation of all the patterns

// ============================================
// /UserProfile/types/user-profile.types.ts
// ============================================

export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  bio: string;
  createdAt: Date;
}

export interface UserProfileProps {
  userId: string;
  editable?: boolean;
  onUpdate?: (user: User) => void;
}

export interface UserProfileContextType {
  user: User | null;
  isLoading: boolean;
  isEditing: boolean;
  setIsEditing: (editing: boolean) => void;
  updateUser: (data: Partial<User>) => Promise<void>;
}

// ============================================
// /UserProfile/context/UserProfileContext.tsx
// ============================================

import { createContext, useContext, useState, ReactNode } from 'react';
import { useUserData } from '../hooks/useUserData';
import type { User, UserProfileContextType } from '../types/user-profile.types';

const UserProfileContext = createContext<UserProfileContextType | null>(null);

export const useUserProfileContext = () => {
  const context = useContext(UserProfileContext);
  if (!context) {
    throw new Error('useUserProfileContext must be used within UserProfileProvider');
  }
  return context;
};

interface UserProfileProviderProps {
  userId: string;
  children: ReactNode;
}

export const UserProfileProvider = ({ userId, children }: UserProfileProviderProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const { user, isLoading, updateUser } = useUserData(userId);

  const value: UserProfileContextType = {
    user,
    isLoading,
    isEditing,
    setIsEditing,
    updateUser,
  };

  return (
    <UserProfileContext.Provider value={value}>
      {children}
    </UserProfileContext.Provider>
  );
};

// ============================================
// /UserProfile/hooks/useUserData.ts
// ============================================

import { useState, useEffect, useCallback } from 'react';
import { fetchUser, updateUserApi } from '../api/user-profile.api';
import type { User } from '../types/user-profile.types';

export const useUserData = (userId: string) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadUser = async () => {
      try {
        setIsLoading(true);
        const data = await fetchUser(userId);
        setUser(data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load user'));
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, [userId]);

  const updateUser = useCallback(async (data: Partial<User>) => {
    if (!user) return;
    
    const updatedUser = await updateUserApi(user.id, data);
    setUser(updatedUser);
  }, [user]);

  return { user, isLoading, error, updateUser };
};

// ============================================
// /UserProfile/hooks/useUserForm.ts
// ============================================

import { useState, useCallback } from 'react';
import type { User } from '../types/user-profile.types';

export const useUserForm = (initialUser: User | null) => {
  const [formData, setFormData] = useState({
    name: initialUser?.name ?? '',
    email: initialUser?.email ?? '',
    bio: initialUser?.bio ?? '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = useCallback((field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when field changes
    setErrors(prev => ({ ...prev, [field]: '' }));
  }, []);

  const validate = useCallback(() => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const reset = useCallback(() => {
    setFormData({
      name: initialUser?.name ?? '',
      email: initialUser?.email ?? '',
      bio: initialUser?.bio ?? '',
    });
    setErrors({});
  }, [initialUser]);

  return { formData, errors, handleChange, validate, reset };
};

// ============================================
// /UserProfile/api/user-profile.api.ts
// ============================================

import type { User } from '../types/user-profile.types';

const API_BASE = '/api/users';

export const fetchUser = async (userId: string): Promise<User> => {
  const response = await fetch(`${API_BASE}/${userId}`);
  if (!response.ok) throw new Error('Failed to fetch user');
  return response.json();
};

export const updateUserApi = async (userId: string, data: Partial<User>): Promise<User> => {
  const response = await fetch(`${API_BASE}/${userId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update user');
  return response.json();
};

// ============================================
// /UserProfile/components/UserAvatar.tsx
// ============================================

import { useUserProfileContext } from '../context/UserProfileContext';
import styles from '../UserProfile.module.css';

export const UserAvatar = () => {
  const { user, isLoading } = useUserProfileContext();

  if (isLoading) {
    return <div className={styles.avatarSkeleton} />;
  }

  return (
    <img
      src={user?.avatar}
      alt={`${user?.name}'s avatar`}
      className={styles.avatar}
    />
  );
};

// ============================================
// /UserProfile/components/UserInfo.tsx
// ============================================

import { useUserProfileContext } from '../context/UserProfileContext';
import styles from '../UserProfile.module.css';

export const UserInfo = () => {
  const { user, isLoading, isEditing, setIsEditing } = useUserProfileContext();

  if (isLoading) {
    return <div className={styles.infoSkeleton} />;
  }

  return (
    <div className={styles.info}>
      <h2 className={styles.name}>{user?.name}</h2>
      <p className={styles.email}>{user?.email}</p>
      <p className={styles.bio}>{user?.bio}</p>
      
      {!isEditing && (
        <button
          className={styles.editButton}
          onClick={() => setIsEditing(true)}
        >
          Edit Profile
        </button>
      )}
    </div>
  );
};

// ============================================
// /UserProfile/components/UserEditForm.tsx
// ============================================

import { useUserProfileContext } from '../context/UserProfileContext';
import { useUserForm } from '../hooks/useUserForm';
import styles from '../UserProfile.module.css';

export const UserEditForm = () => {
  const { user, isEditing, setIsEditing, updateUser } = useUserProfileContext();
  const { formData, errors, handleChange, validate, reset } = useUserForm(user);

  if (!isEditing) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validate()) {
      await updateUser(formData);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    reset();
    setIsEditing(false);
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.field}>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
        />
        {errors.name && <span className={styles.error}>{errors.name}</span>}
      </div>

      <div className={styles.field}>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
        />
        {errors.email && <span className={styles.error}>{errors.email}</span>}
      </div>

      <div className={styles.field}>
        <label htmlFor="bio">Bio</label>
        <textarea
          id="bio"
          value={formData.bio}
          onChange={(e) => handleChange('bio', e.target.value)}
        />
      </div>

      <div className={styles.actions}>
        <button type="button" onClick={handleCancel}>Cancel</button>
        <button type="submit">Save</button>
      </div>
    </form>
  );
};

// ============================================
// /UserProfile/UserProfile.tsx
// ============================================

import { UserProfileProvider } from './context/UserProfileContext';
import { UserAvatar } from './components/UserAvatar';
import { UserInfo } from './components/UserInfo';
import { UserEditForm } from './components/UserEditForm';
import type { UserProfileProps } from './types/user-profile.types';
import styles from './UserProfile.module.css';

export const UserProfile = ({ userId, editable = true }: UserProfileProps) => {
  return (
    <UserProfileProvider userId={userId}>
      <div className={styles.container}>
        <UserAvatar />
        <UserInfo />
        {editable && <UserEditForm />}
      </div>
    </UserProfileProvider>
  );
};

// ============================================
// /UserProfile/UserProfile.module.css
// ============================================

/*
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
}

.avatarSkeleton {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #e0e0e0;
  animation: pulse 1.5s infinite;
}

.info {
  text-align: center;
  margin-top: 1rem;
}

.name {
  font-size: 1.5rem;
  margin: 0.5rem 0;
}

.email {
  color: #666;
}

.bio {
  margin-top: 1rem;
  line-height: 1.6;
}

.editButton {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
}

.form {
  width: 100%;
  margin-top: 1rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.field input,
.field textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.error {
  color: red;
  font-size: 0.875rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
*/

// ============================================
// /UserProfile/index.ts
// ============================================

export { UserProfile } from './UserProfile';
export { UserProfileProvider, useUserProfileContext } from './context/UserProfileContext';
export { useUserData } from './hooks/useUserData';
export { useUserForm } from './hooks/useUserForm';
export type { User, UserProfileProps, UserProfileContextType } from './types/user-profile.types';

// ============================================
// Usage Example
// ============================================

/*
import { UserProfile } from '@/components/UserProfile';

function App() {
  return (
    <main>
      <UserProfile userId="123" editable />
    </main>
  );
}
*/
