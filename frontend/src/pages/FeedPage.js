import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const FeedPage = () => {
  const { user, logout } = useContext(AuthContext);

  return (
    <div style={{ padding: '20px' }}>
      <h1>Feed</h1>
      <p>Welcome, {user?.username || 'User'}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

export default FeedPage;
