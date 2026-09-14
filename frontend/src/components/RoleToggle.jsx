import React from 'react';

export default function RoleToggle({ currentRole, onRoleChange }) {
  return (
    <div className="role-toggle-container">
      <span className="role-label">Active Role:</span>
      <div className="role-buttons">
        <button
          type="button"
          className={`role-btn ${currentRole === 'resident' ? 'active' : ''}`}
          onClick={() => onRoleChange('resident')}
        >
          Resident
        </button>
        <button
          type="button"
          className={`role-btn ${currentRole === 'responder' ? 'active' : ''}`}
          onClick={() => onRoleChange('responder')}
        >
          First Responder
        </button>
      </div>
    </div>
  );
}
