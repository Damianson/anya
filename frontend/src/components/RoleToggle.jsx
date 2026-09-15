import React from 'react';

export default function RoleToggle({ currentRole, onRoleChange, t = (k) => k }) {
  return (
    <div className="role-toggle-container">
      <span className="role-label">{t('role_label') || 'Active Role:'}</span>
      <div className="role-buttons">
        <button
          type="button"
          className={`role-btn ${currentRole === 'resident' ? 'active' : ''}`}
          onClick={() => onRoleChange('resident')}
        >
          {t('role_resident') || 'Resident'}
        </button>
        <button
          type="button"
          className={`role-btn ${currentRole === 'responder' ? 'active' : ''}`}
          onClick={() => onRoleChange('responder')}
        >
          {t('role_responder') || 'First Responder'}
        </button>
      </div>
    </div>
  );
}
