import React, { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';
import '../styles/feed.css';

const FeedPage = () => {
  const { user, logout } = useContext(AuthContext);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await api.get('/posts/');
      setPosts(response.data.data);
    } catch (err) {
      setError('Failed to load posts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (postId) => {
    try {
      const response = await api.post(`/posts/${postId}/likes/`);
      const { liked } = response.data;

      setPosts((prevPosts) =>
        prevPosts.map((post) => {
          if (post.id === postId) {
            return {
              ...post,
              likes_count: liked ? post.likes_count + 1 : post.likes_count - 1,
              is_liked: liked,
            };
          }
          return post;
        })
      );
    } catch (err) {
      console.error('Failed to like post:', err);
    }
  };

  const handleAddComment = async (postId, text) => {
    try {
      const response = await api.post(`/posts/${postId}/comments/`, { text });
      const newComment = response.data.data;

      setPosts((prevPosts) =>
        prevPosts.map((post) => {
          if (post.id === postId) {
            return {
              ...post,
              comments_count: post.comments_count + 1,
              recent_comments: [...(post.recent_comments || []), newComment],
            };
          }
          return post;
        })
      );
    } catch (err) {
      console.error('Failed to add comment:', err);
    }
  };

  const formatTime = (dateString) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays < 7) return `${diffDays}d`;
    return date.toLocaleDateString();
  };

  const handlePostCreated = (newPost) => {
    setPosts((prevPosts) => [newPost, ...prevPosts]);
  };

  if (loading) {
    return <div className="feed-loading">Loading your feed...</div>;
  }

  return (
    <div className="feed-container">
      <div className="feed-header">
        <h1>Feed</h1>
        <button className="logout-btn" onClick={logout}>Logout</button>
      </div>

      <CreatePost onPostCreated={handlePostCreated} />

      {error && <div className="feed-error">{error}</div>}

      {posts.length === 0 && !error ? (
        <div className="feed-empty">No posts yet. Be the first to post!</div>
      ) : (
        posts.map((post) => (
          <PostCard
            key={post.id}
            post={post}
            currentUser={user}
            onLike={handleLike}
            onAddComment={handleAddComment}
            formatTime={formatTime}
          />
        ))
      )}
    </div>
  );
};

const CreatePost = ({ onPostCreated }) => {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [caption, setCaption] = useState('');
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState('');

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    setImage(file);
    setError('');

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      setError('Please select an image');
      return;
    }

    setPosting(true);
    setError('');

    const formData = new FormData();
    formData.append('image', image);
    formData.append('caption', caption);

    try {
      const response = await api.post('/posts/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      onPostCreated(response.data.data);

      setImage(null);
      setPreview(null);
      setCaption('');
    } catch (err) {
      setError(err.response?.data?.errors?.image?.[0] || 'Failed to create post');
      console.error(err);
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className="create-post-card">
      <h3>Create Post</h3>
      <form onSubmit={handleSubmit}>
        {preview ? (
          <img src={preview} alt="Preview" className="image-preview" />
        ) : (
          <div className="file-input-wrapper">
            <input type="file" accept="image/*" onChange={handleImageChange} />
            <p className="file-input-label">Click to select an image</p>
          </div>
        )}

        {preview && (
          <div className="file-input-wrapper" style={{ padding: '10px', marginBottom: '12px' }}>
            <input type="file" accept="image/*" onChange={handleImageChange} />
            <p className="file-input-label">Change image</p>
          </div>
        )}

        <textarea
          className="caption-input"
          placeholder="Write a caption..."
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
        />

        {error && <div className="create-post-error">{error}</div>}

        <button type="submit" className="create-post-btn" disabled={!image || posting}>
          {posting ? 'Posting...' : 'Share Post'}
        </button>
      </form>
    </div>
  );
};

const PostCard = ({ post, currentUser, onLike, onAddComment, formatTime }) => {
  const [commentText, setCommentText] = useState('');
  const [comments, setComments] = useState(post.recent_comments || []);
  const [showAllComments, setShowAllComments] = useState(false);
  const [allComments, setAllComments] = useState([]);
  const [loadingComments, setLoadingComments] = useState(false);

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    await onAddComment(post.id, commentText);
    setCommentText('');

    const response = await api.get(`/posts/${post.id}/comments/`);
    setComments(response.data.data.slice(-2));
  };

  const handleViewAllComments = async () => {
    if (showAllComments) {
      setShowAllComments(false);
      return;
    }

    setLoadingComments(true);
    try {
      const response = await api.get(`/posts/${post.id}/comments/`);
      setAllComments(response.data.data);
      setShowAllComments(true);
    } catch (err) {
      console.error('Failed to load comments:', err);
    } finally {
      setLoadingComments(false);
    }
  };

  const imageUrl = post.image.startsWith('http')
    ? post.image
    : `http://localhost:8000${post.image}`;

  const displayComments = showAllComments ? allComments : comments;

  return (
    <div className="post-card">
      <div className="post-header">
        <span className="post-username">{post.user.username}</span>
        <span className="post-time">{formatTime(post.created_at)}</span>
      </div>

      <img src={imageUrl} alt={post.caption || 'Post'} className="post-image" />

      <div className="post-actions">
        <button
          className={`action-btn ${post.is_liked ? 'liked' : ''}`}
          onClick={() => onLike(post.id)}
        >
          {post.is_liked ? '♥' : '♡'}
        </button>
      </div>

      <div className="post-info">
        <div className="likes-count">
          {post.likes_count} {post.likes_count === 1 ? 'like' : 'likes'}
        </div>

        {post.caption && (
          <div className="post-caption">
            <span className="caption-username">{post.user.username}</span>
            {post.caption}
          </div>
        )}

        {post.comments_count > 2 && !showAllComments && (
          <button className="view-all-comments" onClick={handleViewAllComments}>
            {loadingComments ? 'Loading...' : `View all ${post.comments_count} comments`}
          </button>
        )}

        {displayComments.map((comment) => (
          <div key={comment.id} className="comment-item">
            <span className="comment-username">{comment.user.username}</span>
            {comment.text}
          </div>
        ))}

        {showAllComments && (
          <button className="view-all-comments" onClick={handleViewAllComments}>
            Hide comments
          </button>
        )}
      </div>

      <form className="add-comment" onSubmit={handleSubmitComment}>
        <input
          type="text"
          placeholder="Add a comment..."
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
        />
        <button type="submit" disabled={!commentText.trim()}>
          Post
        </button>
      </form>
    </div>
  );
};

export default FeedPage;
