import { createBrowserRouter } from "react-router";
import Root from "./Root";
import Home from "./pages/Home";
import StockDetail from "./pages/StockDetail";
import Performance from "./pages/Performance";
import About from "./pages/About";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "stock/:symbol", Component: StockDetail },
      { path: "performance", Component: Performance },
      { path: "about", Component: About },
    ],
  },
]);
