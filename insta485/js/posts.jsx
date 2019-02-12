import React from 'react';
import PropTypes from 'prop-types';
import Likes from './likes';

class Posts extends React.Component {

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { postid: 0, img_url: "", owner: "", age: 0, owner_show_url: "", owner_img_url: "", post_show_url: "", url: "" };
  }

  componentDidMount() {
    // Call REST API to get post data
    fetch(this.props.url, { credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText);
      return response.json();
    })
    .then((data) => {
      this.setState({
        postid: data.postid,
        img_url: data.img_url,
        owner: data.owner,
        age: data.age,
        owner_show_url: data.owner_show_url,
        owner_img_url: data.owner_img_url,
        post_show_url: data.post_show_url,
        url: data.url
      });
    })
    .catch(error => console.log(error));  // eslint-disable-line no-console
  }

  render() {
    // Render post
    return (
      <div className="posts">
        <img src="{this.state.owner.img_url}" alt = "Profile Pic" width ="20" height="20" />
		<a href="/u/{this.state.owner}/"> <b> {this.state.owner} </b> </a>
        <p> and hi! </p>
        
        <p><Likes url="/api/v1/p/<postid_slug>/likes/" /></p>
      </div>
    );
  }
}


Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
