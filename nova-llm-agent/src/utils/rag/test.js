require('dotenv').config();
const { Pinecone } = require('@pinecone-database/pinecone');

const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY,
  controllerHostUrl: `https://controller.${process.env.PINECONE_ENV}.pinecone.io`,
});

(async () => {
  try {
    const indexes = await pinecone.listIndexes();
    console.log("Indexes:", indexes);
  } catch (e) {
    console.error("Failed to connect to Pinecone:", e.message);
    if (e.response && e.response.data) {
      console.error("Pinecone response data:", e.response.data);
    }
  }
})();
