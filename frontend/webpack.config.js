const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');


module.exports = {
  entry: './src/index.ts',
  output: {
    filename: 'index.js',
    path: path.resolve(__dirname, 'lib'),
    library: 'hsfiles_jupyter',
    libraryTarget: 'amd'
  },
  resolve: {
    extensions: ['.ts', '.js'],
    alias: {
      'hsfiles_jupyter': path.resolve(__dirname, 'src')
    }
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      {
        test: /\.svg$/,
        use: 'svg-url-loader'
      }
    ]
  },
  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'package.json', to: '.' }
      ]
    })
  ],
  externals: [
    '@jupyterlab/application',
    '@jupyterlab/apputils',
    '@jupyterlab/filebrowser',
    'yjs'
  ]
};
