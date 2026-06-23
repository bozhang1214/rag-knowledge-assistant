/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://shared-backend:8002/:path*',  // 后端服务名，PROJECT_ID=2
      },
    ];
  },
};

module.exports = nextConfig;
