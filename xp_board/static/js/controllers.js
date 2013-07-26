// var usernames = [
//   'atribone', 'imalison', 'anthony', 'sraveend', 'dersek', 'ssridhar',
//   'yoann', 'selston', 'cheng', 'bthiell', 'arvin', 'ychan', 'yli',
//   'clee', 'matthew', 'ywchen', 'joshua'
// ];
// $scope.statuses = ["New", "Assigned", "In Review", "Ship-It", "On Prod"]

TicketsByStatusCtrl = ['$scope', 'TicketData', function ($scope, TicketData) {
  debugger;
  $scope.ticketsByStatus = _.groupBy(TicketData.tickets, 'status');
}];

TicketsByOwnerCtrl = ['$scope', 'TicketData', function UserStatusCtrl($scope, TicketData) {
  $scope.ticketsByOwner = _.groupBy(TicketData.tickets, 'owner');
}];


ReviewsByUserCtrl = ['$scope', function ReviewStatusCtrl($scope) {

}];
