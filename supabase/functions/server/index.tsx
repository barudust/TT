import { Hono } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import * as kv from "./kv_store.tsx";
import { 
  getStockList, 
  getStockDetail, 
  getHistoricalData, 
  getPerformanceMetrics,
  getAllPerformanceMetrics 
} from "./stock_data.tsx";

const app = new Hono();

// Enable logger
app.use('*', logger(console.log));

// Enable CORS for all routes and methods
app.use(
  "/*",
  cors({
    origin: "*",
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
  }),
);

// Health check endpoint
app.get("/make-server-8ca8c1f7/health", (c) => {
  return c.json({ status: "ok" });
});

// Get list of all stocks with current signals
app.get("/make-server-8ca8c1f7/stocks", async (c) => {
  try {
    const stocks = await getStockList();
    return c.json({ success: true, data: stocks });
  } catch (error) {
    console.error("Error fetching stock list:", error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get detailed information for a specific stock
app.get("/make-server-8ca8c1f7/stocks/:symbol", async (c) => {
  try {
    const symbol = c.req.param("symbol");
    const detail = await getStockDetail(symbol);
    return c.json({ success: true, data: detail });
  } catch (error) {
    console.error(`Error fetching detail for ${c.req.param("symbol")}:`, error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get historical price data for a stock
app.get("/make-server-8ca8c1f7/stocks/:symbol/history", async (c) => {
  try {
    const symbol = c.req.param("symbol");
    const days = parseInt(c.req.query("days") || "30");
    const history = await getHistoricalData(symbol, days);
    return c.json({ success: true, data: history });
  } catch (error) {
    console.error(`Error fetching history for ${c.req.param("symbol")}:`, error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get performance metrics for a specific stock
app.get("/make-server-8ca8c1f7/stocks/:symbol/metrics", async (c) => {
  try {
    const symbol = c.req.param("symbol");
    const metrics = await getPerformanceMetrics(symbol);
    return c.json({ success: true, data: metrics });
  } catch (error) {
    console.error(`Error fetching metrics for ${c.req.param("symbol")}:`, error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get performance metrics for all stocks
app.get("/make-server-8ca8c1f7/metrics", async (c) => {
  try {
    const metrics = await getAllPerformanceMetrics();
    return c.json({ success: true, data: metrics });
  } catch (error) {
    console.error("Error fetching all metrics:", error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

Deno.serve(app.fetch);