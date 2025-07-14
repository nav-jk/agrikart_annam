import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Ensure Link is imported
import api from '../api/api';
import '../styles/SignupFarmer.css'; // New styles for SignupFarmer

const SignupFarmer = () => {
  // Initialize form state with fields expected by the backend
  const [form, setForm] = useState({ 
    username: '', 
    email: '', 
    phone_number: '', // Changed from 'phone' for consistency with potential backend
    password: '', 
    name: '', // Farmer's name
    address: '' 
  });
  const [loading, setLoading] = useState(false); // State for loading indicator
  const [signupError, setSignupError] = useState(''); // State for error messages

  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setSignupError(''); // Clear any previous error when user starts typing
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); // Start loading
    setSignupError(''); // Clear previous errors

    try {
      // Send the form data to the farmer signup API
      await api.post('/api/v1/auth/signup/farmer/', {
        username: form.username,
        email: form.email,
        phone_number: form.phone_number, // Ensure this matches your API expectation
        password: form.password,
        name: form.name, // Farmer's specific field
        address: form.address,
        is_farmer: true, // Explicitly set role for farmer signup
      });

      // On successful signup, navigate to the login page
      alert('Farmer account created successfully! Please log in.'); // Simple alert for success
      navigate('/login');
    } catch (err) {
      console.error('Farmer signup error:', err.response?.data || err.message);
      // Display a user-friendly error message on the UI
      if (err.response && err.response.data) {
        // Try to get specific error messages from the backend
        const errors = err.response.data;
        if (errors.username) {
          setSignupError(`Username: ${errors.username[0]}`);
        } else if (errors.email) {
          setSignupError(`Email: ${errors.email[0]}`);
        } else if (errors.phone_number) { // Use phone_number for error if that's the field name
          setSignupError(`Phone Number: ${errors.phone_number[0]}`);
        } else if (errors.password) {
          setSignupError(`Password: ${errors.password[0]}`);
        } else if (errors.name) {
            setSignupError(`Farmer Name: ${errors.name[0]}`);
        } else if (errors.address) {
            setSignupError(`Address: ${errors.address[0]}`);
        } else if (errors.detail) { // Generic detail error
          setSignupError(errors.detail);
        } else {
          setSignupError('Signup failed. Please check your details and try again.');
        }
      } else {
        setSignupError('Signup failed. A network error occurred or the server is unreachable.');
      }
    } finally {
      setLoading(false); // Stop loading
    }
  };

  return (
    <div className="page-wrapper signup-farmer-page-wrapper">
      <div className="signup-farmer-container">
        <form onSubmit={handleSubmit} className="signup-farmer-form">
          <div className="signup-farmer-header">
            <h2 className="signup-farmer-title">Join AgriKart.ai as a Farmer</h2>
          </div>

          {signupError && <p className="signup-farmer-error-message">{signupError}</p>}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              value={form.username}
              onChange={handleChange}
              placeholder="Choose a username"
              required
              className="form-input"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="your@email.com"
              required
              className="form-input"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone_number">Phone Number</label>
            <input
              id="phone_number"
              name="phone_number" // Make sure this name matches your backend's expected field
              type="tel" // Use type="tel" for phone numbers
              value={form.phone_number}
              onChange={handleChange}
              placeholder="e.g., +91 9876543210"
              required
              className="form-input"
              autoComplete="tel"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Create a strong password"
              required
              className="form-input"
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="address">Farm Address</label>
            <textarea
              id="address"
              name="address"
              value={form.address}
              onChange={handleChange}
              placeholder="Your full farm address including village/city, district, state, and pin code"
              required
              rows="3" // Make textarea bigger
              className="form-input form-textarea"
              autoComplete="street-address"
            ></textarea>
          </div>

          <button type="submit" className="signup-farmer-button" disabled={loading}>
            {loading ? 'Registering...' : 'Sign Up as Farmer'}
          </button>

          <p className="signup-farmer-footer">
            Already have an account? <Link to="/login" className="login-link">Sign In here</Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default SignupFarmer;
