import { createBrowserRouter } from "react-router";
import Root from "./Root";
import Home from "./pages/Home";
import StockDetail from "./pages/StockDetail";
import Performance from "./pages/Performance";
import About from "./pages/About";
import Help from "./pages/Help";
import Aprende from "./pages/Aprende";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "stock/:symbol", Component: StockDetail },
      { path: "performance", Component: Performance },
      { path: "aprende", Component: Aprende },
      { path: "ayuda", Component: Help },
      { path: "about", Component: About },
    ],
  },
]);
