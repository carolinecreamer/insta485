import React from 'react';
import PropTypes from 'prop-types';


class Likes extends React.Component {
  /* Display number of likes a like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { num_likes: 0, logname_likes_this: false };
    this.handleClick = this.handleClick.bind(this);
  }

  componentDidMount() {
    // Call REST API to get number of likes 
    fetch(this.props.url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          num_likes: data.likes_count,
          logname_likes_this: data.logname_likes_this,
          button_text: (data.logname_likes_this ? 'unlike' : 'like'),
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }

  handleClick(event) {
    // Call REST API to add or remove a like
    event.preventDefault();
    fetch(this.props.url, {
      credentials: 'include',
      method: (this.state.logname_likes_this === 1 ? 'DELETE' : 'POST'),
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json;
      })
      .then(() => {
        fetch(this.props.url, { credentials: 'same-origin' })
          .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
          })
          .then((data) => {
            this.setState({
              num_likes: data.likes_count,
              logname_likes_this: data.logname_likes_this,
              button_text: (data.logname_likes_this ? 'unlike' : 'like'),
            });
          });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }

  render() {
    // Render number of likes
    return (
      <div className="likes">
        <button id='like-unlike-button' onClick={this.handleClick}>
          <p>{this.state.button_text} </p>
        </button>
        <p>{this.state.num_likes} like{this.state.num_likes !== 1 ? 's' : ''}</p>
      </div>
    );
  }
}


Likes.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Likes;

