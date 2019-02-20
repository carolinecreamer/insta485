import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
  constructor(props) {
    super(props);
    this.state = { comments: [{ owner: '', text: '', owner_show_url: '' }], value: '' };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    fetch(this.props.url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const commentList = [];
        for (let i = 0; i < data.comments.length; i += 1) {
          commentList.push({ owner: data.comments[i].owner,
            text: data.comments[i].text,
            owner_show_url: data.comments[i].owner_show_url });
        }
        this.setState({
          comments: commentList,
          value: '',
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  handleSubmit(event) {
    event.preventDefault();
    fetch(this.props.url, {
      credentials: 'include',
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: this.state.value,
      }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const joined = this.state.comments.concat({ owner: data.owner,
          text: data.text,
          owner_show_url: data.owner_show_url });
        this.setState({
          comments: joined,
          value: '',
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }
  render() {
    return (
      <div className="comments">
        {this.state.comments.map(item => (
          <p><a href={item.owner_show_url}><strong>{item.owner}</strong></a> {item.text}</p>
        ))}
        <form id="comment-form" onSubmit={this.handleSubmit}>
          <input type="text" value={this.state.value} onChange={this.handleChange} />
        </form>
      </div>
    );
  }
}

Comments.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Comments;
