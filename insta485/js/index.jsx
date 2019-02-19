import React from 'react';
import PropTypes from 'prop-types';
import Posts from './posts';
import InfiniteScroll from 'react-infinite-scroll-component';

class Index extends React.Component {
	
	constructor(props) {
	  	super(props);
	    this.state = { results: [], next: "", url : "" };
  	}
  	componentDidMount() {
  		fetch(this.props.url, { credentials: 'same-origin' })
  		.then((response) => {
  			if (!response.ok) throw Error(response.statusText);
  			return response.json();
  		})
  		.then((data) => {
  			this.setState({
  				results : data.results,
        		next : data.next,
        		url : data.url,
  			});
  		})
  		.catch(error => console.log(error));
  	}
   fetchData() {
        fetch(this.state.next, { credentials: 'same-origin' })
              .then((response) => {
                  if (!response.ok) throw Error(response.statusText);
                  return response.json();
                })
                .then((data) => {
                  this.state.results.concat(data.results)
                })
    }
  	render() {
  		return (
        <div>
        <InfiniteScroll
          dataLength = {this.state.results.length}
          hasMore= {this.state.next !== ""}
          loadMore = {fetchData}
        >
  			<div className="index">
	  			{this.state.results.map((item, index) => (
	  				<Posts url={item.url} key={'mykey' + index}/>
	  			))}
	  		</div>
        </InfiniteScroll>
        </div>
	    );
  	}
}

Index.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Index;