import React from 'react';
import ReactDOM from 'react-dom';
import Likes from './likes';

ReactDOM.render(
<Likes url="/api/v1/p/<postid_slug>/likes/" />,
  document.getElementById('reactEntry'),
);

