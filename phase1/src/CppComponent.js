import React from 'react';

class CppComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { result: "" };
  }

  componentDidMount() {
    fetch('http://localhost:5000/api/run-cpp')
      .then(response => response.text())
      .then(result => this.setState({ result }))
      .catch(error => console.error(error));
  }

  render() {
    return (
      <div>
      </div>
    );
  }
}

export default CppComponent;
