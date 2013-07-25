var XPBoard = angular.module('XPBoard', []).config(
  ['$routeProvider', '$locationProvider',
   function($routeProvider, $locationProvider) {
     var templateRoot = "/static/js/view_templates"
     $routeProvider("/ticket_status", {
       templateUrl: templateRoot + "board.html",
       controller: TicketStatusCtrl
     }).otherwise(
       redirectTo: "/ticket_status"
     )
  }]
);
