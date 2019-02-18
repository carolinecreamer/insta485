import React from 'react';
import PropTypes from 'prop-types';
import Likes from './likes';
import Comments from './comments';


class Posts extends React.Component {

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { img_url: "", owner: "", age: 0, owner_show_url: "", owner_img_url: "", post_show_url: "", url: ""};
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
    let likes_url = this.props.url.concat("likes/");
    let comments_url = this.props.url.concat("comments/")

    return (
      <div className="posts">

        <div className="box">
        <img src={this.state.owner_img_url} alt = "Profile Pic" width ="20" height="20" />

        <p> <a href={this.state.owner_show_url}> <b> {this.state.owner} </b> </a>

        <a href={this.state.post_show_url}> <span style={{"float" : "right"}}> {this.state.age} </span> </a></p>

        <br></br>
        
        <img src={this.state.img_url} alt="Post {this.state.img_url}" width = "500" height="500"/> 
        <br></br>
        <Likes url={likes_url}/>
        <p> comments </p>
        <Comments url ={comments_url}/>
        </div>
      </div>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};
export default Posts;