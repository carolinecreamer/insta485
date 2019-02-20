import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Posts from './posts';


class Index extends React.Component {
  constructor(props) {
    super(props);
    this.state = { results: [], next: '', url: '' };
    this.fetchData = this.fetchData.bind(this);
    if (performance.navigation.type === 2) {
      this.state = history.state;
    }
  }
  componentDidMount() {
    if (performance.navigation.type === 2) {
      return;
    }
    fetch(this.props.url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          results: data.results,
          next: data.next,
          url: data.url,
        });
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }
  fetchData() {
    fetch(this.state.next, { credentials: 'same-origin' })
      .then(response => response.json())
      .then((data) => {
        this.setState({
          results: this.state.results.concat(data.results),
          next: data.next,
          url: data.url,
        });
        history.replaceState(this.state, {});
      })
      .catch(error => console.log(error)); // eslint-disable-line no-console
  }

  render() {
    return (
      <div>
        <InfiniteScroll
          dataLength={this.state.results.length}
          hasMore={this.state.next !== ''}
          next={this.fetchData}
          link={this.state.next}
          results={this.state.results}
        >
          <div className="index">
            {this.state.results.map((item, index) => (
              <Posts url={item.url} key={`mykey${index}`} />
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
