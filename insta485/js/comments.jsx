import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
	constructor(props) {
		super(props);
		this.state = { comments: [ {owner: "", text: "", owner_show_url: ""} ] };
	}

	componentDidMount() {
		fetch(this.props.url, { credentials: 'same-origin' })
		.then((response) => {
			if (!response.ok) throw Error(response.statusText);
			return response.json();
		})
		.then((data) => {
			let comment_list = []
			for (let i = 0; i < data.comments.length; i++) {
				comment_list.push({owner: data.comments[i].owner, text: data.comments[i].text, owner_show_url: data.comments[i].owner_show_url})
			}
			this.setState({
				comments: comment_list,
			});
		})
		.catch(error => console.log(error));
	}

	render() {
		return (
			<div className="comments">
				{this.state.comments.map(item => (
					<p><a href = {item.owner_show_url}><strong>{item.owner}</strong></a> {item.text}</p>
				))}
			</div>
		);
	}
}

Comments.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Comments;