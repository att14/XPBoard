var XPBoard = angular.module('XPBoard', []).config(
  ['$routeProvider', '$locationProvider',
   function($routeProvider, $locationProvider) {
     var templateRoot = "/static/js/view_templates/";
     $routeProvider.when("/tickets_by_status", {
       templateUrl: templateRoot + "tickets_by_status.html",
       controller: TicketsByStatusCtrl
     }).otherwise({
       redirectTo: "/tickets_by_status"
     })
  }]
);
