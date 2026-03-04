import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Sidebar } from './Sidebar';

// ---------------------------------------------------------------------------
// BDD Scenarios:
//   Feature: Dark mode toggle admin-only
//
//   Scenario: Admin user sees theme toggle
//     Given user role is 'admin'
//     When sidebar renders
//     Then theme toggle button is visible
//
//   Scenario: Leader user does not see theme toggle
//     Given user role is 'leader'
//     When sidebar renders
//     Then theme toggle button is NOT visible
//
//   Scenario: Member user does not see theme toggle
//     Given user role is 'member'
//     When sidebar renders
//     Then theme toggle button is NOT visible
// ---------------------------------------------------------------------------

const mockLogout = vi.fn();

vi.mock('../../context/AuthContext', () => ({
    useAuth: () => ({
        user: { email: 'test@example.com' },
        logout: mockLogout,
    }),
}));

const mockProfile = { id: '1', email: 'test@example.com', role: 'leader', created_at: '', last_login: '' };

vi.mock('../../hooks/useCurrentUser', () => ({
    useCurrentUser: () => ({
        profile: mockProfile,
        isLoading: false,
        isError: false,
    }),
}));

// Mock next-themes
vi.mock('next-themes', () => ({
    useTheme: () => ({ theme: 'light', setTheme: vi.fn() }),
}));

const renderSidebar = () => {
    return render(
        <BrowserRouter>
            <Sidebar />
        </BrowserRouter>
    );
};

describe('Sidebar ThemeToggle visibility', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockProfile.role = 'leader';
    });

    it('shows theme toggle for admin role', () => {
        // Arrange
        mockProfile.role = 'admin';

        // Act
        renderSidebar();

        // Assert
        expect(screen.getByTitle(/switch to dark mode/i)).toBeInTheDocument();
    });

    it('hides theme toggle for leader role', () => {
        // Arrange
        mockProfile.role = 'leader';

        // Act
        renderSidebar();

        // Assert
        expect(screen.queryByTitle(/switch to dark mode/i)).not.toBeInTheDocument();
    });

    it('hides theme toggle for member role', () => {
        // Arrange
        mockProfile.role = 'member';

        // Act
        renderSidebar();

        // Assert
        expect(screen.queryByTitle(/switch to dark mode/i)).not.toBeInTheDocument();
    });
});
